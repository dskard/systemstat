import argparse
import ast
import logging
import requests
import sys

from . import systemstat
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class SutStat(systemstat.SystemStat):
    def __init__(
        self,
        url="http://localhost:6969",
        request_args={},
        response_status_min=100,
        response_status_max=599,
        sleep=1.0,
        wait=30,
        **kwargs,
    ):
        super(SutStat, self).__init__(sleep=sleep, wait=wait, **kwargs)

        self._url = url
        self._request_args = request_args
        self._response_status_min = response_status_min
        self._response_status_max = response_status_max

        self.logger = logging.getLogger(__name__)

        self.logger.info("url: {}".format(url))

    def is_ready(self):
        """check if the system is ready (accepting requests)"""

        ping_url = self._url

        if "verify" in self._request_args and self._request_args["verify"] is False:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        try:
            # query the system to see if it is up.
            response = requests.get(ping_url, **self._request_args)
        except requests.exceptions.ConnectionError:
            self.logger.info("waiting for sut server to respond at {}".format(ping_url))
            # wait and poll again
            return False

        if (
            response.status_code >= self._response_status_min
            and response.status_code <= self._response_status_max
        ):
            # system is up
            self.logger.info("System under test is up at {}".format(ping_url))
            return True
        else:
            # response was not "ok", log error details
            self.logger.info(
                (
                    "System under test responded at "
                    + '"{}" with error:\n{}\n{}\n{}'.format(
                        ping_url, response.status_code, response.headers, response.text
                    )
                )
            )

        # wait and poll again
        return False


class DictArgAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):

        # get data that was previously saved at this destination.
        # if there was no data, start with an empty dictionary.
        d = getattr(namespace, self.dest)
        if d is None:
            d = {}

        # check the format of the value
        if len(values) <= 2:
            raise ValueError(f'expected form "KEY=VALUE": {values}')

        # parse the value and save the key and value in the destination.
        k, v = values.split("=", 1)
        d[k] = ast.literal_eval(v)
        setattr(namespace, self.dest, d)


class SutStatTool(SutStat, systemstat.SystemStatTool):
    def __init__(self, logfile="sutstat.log", **kwargs):
        super(SutStatTool, self).__init__(logfile=logfile)

        self.logger = logging.getLogger(__name__)

        self.command_parser.add_argument(
            "--request-arg",
            help="additional argument for the http request in the form of 'KEY=VALUE'",
            metavar="KEY=VALUE",
            dest="request_args",
            action=DictArgAction,
            default={},
        )

        self.command_parser.add_argument(
            "--response-status-max",
            help="maximum response status code for the request to be considered successful (range 100-599)",
            action="store",
            dest="response_status_max",
            default=599,
            type=int,
        )

        self.command_parser.add_argument(
            "--response-status-min",
            help="minimum response status code for the request to be considered successful (range 100-599)",
            action="store",
            dest="response_status_min",
            default=100,
            type=int,
        )

        self.command_parser.add_argument(
            "--url",
            help="url of the sut server being waited on",
            action="store",
            dest="url",
            default="http://localhost:6969",
            type=str,
        )

        # parse command line and config file options
        self.parse_options()

        # override SutStat class defaults with command line defaults
        self._url = self.options.url
        self._request_args = self.options.request_args
        self._response_status_min = self.options.response_status_min
        self._response_status_max = self.options.response_status_max

        # start logging
        self.start_logging()


def cli():

    tool = SutStatTool()

    tool.logger.info("checking status of {}".format(tool.options.url))

    system_ready = tool.wait_until_ready()

    if system_ready:
        status = 0
    else:
        status = 1

    tool.logger.debug("exiting")

    sys.exit(status)
