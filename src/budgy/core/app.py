import argparse
import datetime
import logging
import os.path
import sys

from budgy import __version__ as BUDGY_VERSION

class BudgyApp(object):
    def __init__(self, app_name):
        self._app_name = app_name
        self._parser:argparse.ArgumentParser = self._create_parser()
        self._add_command_args()
        self._args = self.parse_command_line()


    @property
    def arg_parser(self):
        return self._parser

    def _create_parser(self):
        return argparse.ArgumentParser(self._app_name)

    def _add_command_args(self):
        """
        Override this command to add args to self._parser
        :return: None
        """
        pass

    def parse_command_line(self):
        return self._parser.parse_args()


    def _create_app_header(self):
        header = ''
        header += '##############################\n'
        header += '#\n'
        header += f'# {os.path.basename((sys.argv[0]))}\n'
        header += f'# budgy {BUDGY_VERSION}\n'
        header += f'# Start Time: {datetime.datetime.now()}\n'
        header += '#\n'
        header += '##############################\n'

        return header

    def print_app_header(self):
        header = self._create_app_header()
        print(header)

    def log_app_header(self):
        header = self._create_app_header()
        for line in header.splitlines():
            logging.info(line)

    def run(self):
        pass