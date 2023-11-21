import argparse
import logging


logging.basicConfig(handlers=[logging.StreamHandler(), logging.FileHandler('budgy-importer.log')], level=logging.INFO)

from pathlib import Path

import budgy
from budgy.app import BudgyApp
from budgy import BudgyDatabase

class ImporterApp(BudgyApp):
    def __init__(self):
        super().__init__('Budgy Data Importer')
        self._db = BudgyDatabase(self._args.db)

    def _add_command_args(self):
        parser:argparse.ArgumentParser = self.arg_parser
        parser.add_argument('--db', type=Path, required=True, help='Path to sqlite3 database. Will be created if it '
                                                                   'does not exist')
        parser.add_argument('datafiles', nargs='+', help='One or more datafiles to import')

    def run(self):
        nrecords0 = self._db.count_records()
        if nrecords0 > 0:
            logging.info(f'Database already contains {nrecords0} records')
        for datafile in self._args.datafiles:
            logging.info(f'Importing {datafile}...')
            records = budgy.load_ofx_file(datafile)
            self._db.merge_records(records)
        nrecords1 = self._db.count_records()
        logging.info(f'Database now contains {nrecords1} records')
        new_records = nrecords1 - nrecords0
        if new_records > 0:
            logging.info(f' - Added {new_records} records')
        else:
            logging.info(' - No new records added.')


def main():
    myapp = ImporterApp()
    myapp.run()

if __name__ == '__main__':
    main()
