# systemstat
use http requests to check the status of a system

## Installation

```bash
pip install systemstat
```

Or from this repo:
```bash
pip install git+https://github.com/dskard/systemstat.git
```

## Example Usage:

Use `gridstat3` to check if a Selenium Grid 3 has nodes attached and is ready to accept requests
```bash
$ gridstat3 --wait 4 --url http://localhost:4444 --verbose --stdout

2022-08-21 18:07:06,714 starting gridstat3
2022-08-21 18:07:06,714 command line options: ['--wait', '4', '--url', 'http://localhost:4444', '--verbose', '--stdout']
2022-08-21 18:07:06,714 checking status of http://localhost:4444
2022-08-21 18:07:06,714 starting at 2022-08-21 18:07:06.714839
2022-08-21 18:07:06,714 ending at 2022-08-21 18:07:10.714839
2022-08-21 18:07:06,721 hub is up at http://localhost:4444/grid/api/hub
2022-08-21 18:07:06,721 2 of 2 nodes are attached
2022-08-21 18:07:06,721 all nodes are attached
2022-08-21 18:07:06,721 2 of 2 nodes are ready
2022-08-21 18:07:06,721 all nodes are ready
```

Use `gridstat4` to check if a Selenium Grid 4 has nodes attached and is ready to accept requests
```bash
$ gridstat4 --wait 4 --url http://localhost:4444 --verbose --stdout

2022-08-21 18:48:47,497 starting gridstat4
2022-08-21 18:48:47,497 command line options: ['--wait', '4', '--url', 'http://localhost:4444', '--verbose', '--stdout']
2022-08-21 18:48:47,497 checking status of http://localhost:4444
2022-08-21 18:48:47,497 starting at 2022-08-21 18:48:47.497451
2022-08-21 18:48:47,497 ending at 2022-08-21 18:48:51.497451
2022-08-21 18:48:47,545 hub is up at http://localhost:4444/wd/hub/status
2022-08-21 18:48:47,545 all nodes are ready
```

Use `sutstat` to check if a system is listening on port `4444`
```bash
$ sutstat --wait 4 --url http://localhost:4444 --verbose --stdout

2022-08-21 18:08:25,344 starting sutstat
2022-08-21 18:08:25,344 command line options: ['--wait', '4', '--url', 'http://localhost:4444', '--verbose', '--stdout']
2022-08-21 18:08:25,345 checking status of http://localhost:4444
2022-08-21 18:08:25,345 starting at 2022-08-21 18:08:25.345155
2022-08-21 18:08:25,345 ending at 2022-08-21 18:08:29.345155
2022-08-21 18:08:25,359 System under test is up at http://localhost:4444
```

## Development

Creating a Python virtual environment:
```bash
make pyenv
```

Installing the development dependencies and current version of the library:
```bash
make install
```

Running the test cases:
```bash
make test
```

Running the command line tools through the development environment:
```bash
poetry run gridstat3 --wait 4 --url http://localhost:4444 --verbose --stdout
poetry run gridstat4 --wait 4 --url http://localhost:4444 --verbose --stdout
poetry run sutstat --wait 4 --url http://localhost:8080 --verbose --stdout
```

Clean logs and Python cache files
```bash
make clean
```
