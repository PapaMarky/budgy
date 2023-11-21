__version__='1.0.0'

import logging
from pathlib import Path

import ofxtools
from ofxtools.Parser import OFXTree

ofxtools_logger = logging.getLogger('ofxtools')
ofxtools_logger.setLevel(logging.ERROR)
ofxparser_logger = logging.getLogger('ofxtools.Parser')
ofxparser_logger.setLevel(logging.ERROR)
from budgy.database import BudgyDatabase
from budgy import importer


def load_ofx_file(ofxfile:Path):
    parser = OFXTree()
    parser.parse(ofxfile)
    ofx = parser.convert()
    records = []
    for statement in ofx.statements:
        is_checking = isinstance(statement, ofxtools.models.bank.stmt.STMTRS)
        for txn in statement.transactions:
            checknum = txn.checknum if is_checking else ''
            if checknum is None:
                checknum = ""
            record = {
                'type': txn.trntype,
                'posted': str(txn.dtposted),
                'amount': float(txn.trnamt),
                'fitid': int(txn.fitid),
                'name': txn.name,
                'memo': txn.memo,
                'checknum': checknum
            }
            records.append(record)
    return records