import logging
import requests
import sys

from . import systemstat


class GridStat3(systemstat.SystemStat):
    def __init__(
        self, url="http://localhost:4444", nodes=2, sleep=1.0, wait=30, **kwargs
    ):
        super(GridStat3, self).__init__(sleep=sleep, wait=wait, **kwargs)

        self._url = url
        self._nodes = nodes

        self.logger = logging.getLogger(__name__)

        self.logger.info("url: {}".format(url))
        self.logger.info("nodes: {}".format(nodes))

    def is_ready(self):
        """check if selenium grid is ready

        system ready means:
        1. accepting requests
        2. all nodes attached
        3. all nodes free
        """

        grid_api_hub_url = self._url + "/grid/api/hub"

        try:
            # query the selenium grid server to see if the nodes have attached.
            response = requests.get(grid_api_hub_url)
        except requests.exceptions.ConnectionError:
            self.logger.info(f"waiting for hub to respond at {grid_api_hub_url}")
            # wait and poll again
            return False

        if response.ok:
            # hub is up
            self.logger.info(f"hub is up at {grid_api_hub_url}")

            # check if nodes are attached
            slotCounts = response.json()["slotCounts"]

            self.logger.info(
                f'{slotCounts["total"]} of {self._nodes} nodes are attached'
            )

            if slotCounts["total"] == self._nodes:
                # nodes are attached
                self.logger.info("all nodes are attached")

                # check if nodes are ready
                self.logger.info(
                    f'{slotCounts["free"]} of {self._nodes} nodes are ready'
                )

                if slotCounts["free"] == self._nodes:
                    # nodes are ready
                    self.logger.info("all nodes are ready")
                    return True

                else:
                    # nodes are not ready yet
                    self.logger.info(
                        f'waiting on {self._nodes-slotCounts["free"]} \
                            node(s) to be ready'
                    )

            else:
                # nodes are not attached yet
                self.logger.info(
                    f'waiting on {self._nodes-slotCounts["total"]} \
                        node(s) to attach'
                )

        else:
            # response was not "ok", log error details
            self.logger.info(
                f'hub responded at "{grid_api_hub_url}" with error:\
                    \n{response.status_code}\
                    \n{response.headers}\
                    \n{response.text}'
            )

        # wait and poll again
        return False


class GridStat3Tool(GridStat3, systemstat.SystemStatTool):
    def __init__(self, logfile="gridstat3.log", **kwargs):
        super(GridStat3Tool, self).__init__(logfile=logfile)

        self.logger = logging.getLogger(__name__)

        self.command_parser.add_argument(
            "--nodes",
            help="total number of Selenium Grid 3 nodes",
            action="store",
            dest="nodes",
            default=2,
            type=int,
        )

        self.command_parser.add_argument(
            "--url",
            help="url of the Selenium Grid 3 server being waited on",
            action="store",
            dest="url",
            default="http://localhost:4444",
            type=str,
        )

        # parse command line and config file options
        self.parse_options()

        # override GridStat class defaults with command line defaults
        self._url = self.options.url
        self._nodes = self.options.nodes

        # start logging
        self.start_logging()


def cli():

    tool = GridStat3Tool()

    tool.logger.info("checking status of {}".format(tool.options.url))

    system_ready = tool.wait_until_ready()

    if system_ready:
        status = 0
    else:
        status = 1

    tool.logger.debug("exiting")

    sys.exit(status)
