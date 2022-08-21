import logging
import requests
import sys

from . import systemstat


class GridStat4(systemstat.SystemStat):
    def __init__(
        self, url="http://localhost:4444", nodes=2, sleep=1.0, wait=30, **kwargs
    ):
        super(GridStat4, self).__init__(sleep=sleep, wait=wait, **kwargs)

        self._url = url
        self._nodes = nodes

        self.logger = logging.getLogger(__name__)

        self.logger.info("url: {}".format(url))
        self.logger.info("nodes: {}".format(nodes))

    def is_ready(self):
        """check if selenium grid is ready

        system ready means:
        1. accepting requests / grid ready
        2. all nodes attached
        3. all nodes available
        """

        grid_api_hub_url = self._url + "/wd/hub/status"

        try:
            # query the selenium grid server to see if the nodes have attached.
            response = requests.get(grid_api_hub_url)
        except requests.exceptions.ConnectionError:
            self.logger.info(
                "waiting for hub to respond at {}".format(grid_api_hub_url)
            )
            # wait and poll again
            return False

        if response.ok:
            # hub is up
            self.logger.info("hub is up at {}".format(grid_api_hub_url))

            r = response.json()

            # check if grid is "ready"
            if r["value"]["ready"] is not True:
                # grid is not ready
                self.logger.info("waiting on grid to be ready")

                # wait and poll again
                return False

            # check the number of nodes attached
            node_list = r["value"]["nodes"]
            num_attached_nodes = len(node_list)
            if num_attached_nodes != self._nodes:
                # nodes are not attached yet
                self.logger.info(
                    "waiting on {} node(s) to attach".format(
                        self._nodes - num_attached_nodes
                    )
                )

                # wait and poll again
                return False

            num_unavailable_nodes = 0
            for node_details in node_list:
                if node_details["availability"] != "UP":
                    num_unavailable_nodes += 1

            if num_unavailable_nodes != 0:
                # attached nodes are not available yet
                self.logger.info(
                    "waiting on {} node(s) to attach".format(
                        self._nodes - num_attached_nodes
                    )
                )

                # wait and poll again
                return False

            # nodes are ready
            self.logger.info("all nodes are ready")

            return True


class GridStat4Tool(GridStat4, systemstat.SystemStatTool):
    def __init__(self, logfile="gridstat4.log", **kwargs):
        super(GridStat4Tool, self).__init__(logfile=logfile)

        self.logger = logging.getLogger(__name__)

        self.command_parser.add_argument(
            "--nodes",
            help="total number of Selenium Grid 4 nodes",
            action="store",
            dest="nodes",
            default=2,
            type=int,
        )

        self.command_parser.add_argument(
            "--url",
            help="url of the Selenium Grid 4 server being waited on",
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

    tool = GridStat4Tool()

    tool.logger.info("checking status of {}".format(tool.options.url))

    system_ready = tool.wait_until_ready()

    if system_ready:
        status = 0
    else:
        status = 1

    tool.logger.debug("exiting")

    sys.exit(status)
