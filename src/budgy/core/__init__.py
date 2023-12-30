import logging
from pathlib import Path

import ofxtools
from ofxtools.Parser import OFXTree

ofxtools_logger = logging.getLogger('ofxtools')
ofxtools_logger.setLevel(logging.ERROR)
ofxparser_logger = logging.getLogger('ofxtools.Parser')
ofxparser_logger.setLevel(logging.ERROR)


def load_ofx_file(ofxfile:Path):
    parser = OFXTree()
    parser.parse(ofxfile)
    ofx = parser.convert()
    records = []
    for statement in ofx.statements:
        is_checking = isinstance(statement, ofxtools.models.bank.stmt.STMTRS)
        account = statement.bankacctfrom.acctid if is_checking else statement.ccacctfrom.acctid
        for txn in statement.transactions:
            checknum = txn.checknum if is_checking else ''
            if checknum is None:
                checknum = ""
            record = {
                'fitid': int(txn.fitid),
                'account': account,
                'type': txn.trntype,
                'posted': str(txn.dtposted),
                'amount': float(txn.trnamt),
                'name': txn.name,
                'memo': txn.memo,
                'checknum': checknum,
                'exclude': 0
            }
            records.append(record)
    return records