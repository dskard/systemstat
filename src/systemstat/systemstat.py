import argparse
import datetime
import logging
import os
import sys
import time


class SystemStat(object):
    def __init__(self, sleep=1.0, wait=20, **kwargs):

        # instrumentation for testing
        self._iterations = 0

        self._sleep = sleep
        self._wait = wait

        self.logger = logging.getLogger(__name__)
        self.logger.info("initialization options")
        self.logger.info("sleep: {}".format(sleep))
        self.logger.info("wait: {}".format(wait))

    def wait_until_ready(self):
        """Poll and wait for system to be up

        Return boolean signalling if system came up within self.options.wait
        time.
        """

        try:
            # set the current time and the time when we should exit.
            nowTime = datetime.datetime.now()
            startTime = nowTime
            endTime = nowTime + datetime.timedelta(seconds=self._wait)

            self.logger.info("starting at {}".format(startTime))
            self.logger.info("ending at {}".format(endTime))

            while nowTime < endTime:

                self._iterations += 1
                if self.is_ready():
                    # stop polling, the system is accepting requests.
                    return True
                else:
                    # wait before polling again
                    self.logger.debug("sleeing for {} seconds".format(self._sleep))
                    time.sleep(self._sleep)
                    nowTime = datetime.datetime.now()

            # timed out waiting for system to come up.
            self.logger.info("timed out waiting for system to come up")
            return False

        except Exception as e:
            self.logger.exception(e)
            raise

    def is_ready(self):
        """Check if the system is up.

        In a subclass, override this method with code that checks if the system
        is up and running. If the system is ready, the method should return
        True.  Otherwise, to continue waiting and polling, the method should
        return False.
        """

        return True


class SystemStatTool(SystemStat):
    def __init__(self, logfile="systemstat.log", **kwargs):

        self.options = None
        self.logger = logging.getLogger(__name__)

        self.command_parser = argparse.ArgumentParser()

        self.command_parser.add_argument(
            "--sleep",
            help="seconds to sleep between polling",
            action="store",
            dest="sleep",
            default=1.0,
            type=float,
        )

        self.command_parser.add_argument(
            "--wait",
            help="seconds to wait for the system to launch",
            action="store",
            dest="wait",
            default=20.0,
            type=float,
        )

        self.command_parser.add_argument(
            "--logfile",
            help="name of the logfile",
            action="store",
            dest="logfile",
            default=logfile,
            type=str,
        )

        self.command_parser.add_argument(
            "--logformat",
            help="logging format",
            action="store",
            dest="logformat",
            default="%(asctime)s %(message)s",
            type=str,
        )

        self.command_parser.add_argument(
            "--verbose",
            "-v",
            help="level of logging verbosity",
            dest="verbose",
            default=3,
            action="count",
        )

        self.command_parser.add_argument(
            "--stdout",
            help="print logs to stdout",
            dest="stdout",
            default=False,
            action="store_true",
        )

    def parse_options(self, args=None, namespace=None):

        # parse command line options
        cl_options, cl_unknown = self.command_parser.parse_known_args(args, namespace)

        self.options = cl_options
        self.options.__dict__["remainder"] = cl_unknown

        super(SystemStatTool, self).__init__(
            sleep=self.options.sleep, wait=self.options.wait
        )

    def start_logging(self):

        # setup a log file
        self.options.logfile = os.path.abspath(
            os.path.expanduser(os.path.expandvars(self.options.logfile))
        )

        loglevel = int((6 - self.options.verbose) * 10)

        file_hdlr = logging.FileHandler(self.options.logfile)
        file_hdlr.setFormatter(logging.Formatter(self.options.logformat))
        file_hdlr.setLevel(loglevel)
        self.logger.addHandler(file_hdlr)

        # check if we should print the log to stdout as well
        if self.options.stdout is True:
            out_hdlr = logging.StreamHandler(sys.stdout)
            out_hdlr.setFormatter(logging.Formatter(self.options.logformat))
            out_hdlr.setLevel(loglevel)
            self.logger.addHandler(out_hdlr)

        self.logger.setLevel(loglevel)
        self.logger.info("starting %s" % sys.argv[0])
        self.logger.info("command line options: %s" % sys.argv[1:])

        # print out the parsed options
        self.logger.debug("opts = {}".format(self.options))


def cli():

    tool = SystemStatTool()

    tool.parse_options()
    tool.start_logging()

    system_ready = tool.wait_until_ready()

    if system_ready:
        status = 0
    else:
        status = 1

    tool.logger.debug("exiting")

    sys.exit(status)
