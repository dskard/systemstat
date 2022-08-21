import logging
import requests
import sys

from . import systemstat


class SutStat(systemstat.SystemStat):
    def __init__(self, url="http://localhost:6969", sleep=1.0, wait=30, **kwargs):
        super(SutStat, self).__init__(sleep=sleep, wait=wait, **kwargs)

        self._url = url

        self.logger = logging.getLogger(__name__)

        self.logger.info("url: {}".format(url))

    def is_ready(self):
        """check if the system is ready (accepting requests)"""

        ping_url = self._url

        try:
            # query the system to see if it is up.
            response = requests.get(ping_url)
        except requests.exceptions.ConnectionError:
            self.logger.info("waiting for sut server to respond at {}".format(ping_url))
            # wait and poll again
            return False

        if response.status_code == 200:
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


class SutStatTool(SutStat, systemstat.SystemStatTool):
    def __init__(self, logfile="sutstat.log", **kwargs):
        super(SutStatTool, self).__init__(logfile=logfile)

        self.logger = logging.getLogger(__name__)

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
