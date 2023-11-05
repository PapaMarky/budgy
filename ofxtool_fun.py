import argparse
import sys
from pathlib import Path

import ofxtools

from ofxtools.Parser import OFXTree
# /Users/mark/Downloads/742234ofxdl.qfx - card
# /Users/mark/Downloads/367716ofxdl.qfx - checking
def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument('ofxfile', type=Path, help='Path to ofx file with data')
    return parser.parse_args()

if __name__ == '__main__':
    print('ofxtools tests')
    args = parse_command_line()
    parser = OFXTree()
    parser.parse(args.ofxfile)
    ofx = parser.convert()

    for statement in ofx.statements:
        print('-- Institution --')
        print(f'TYPE: {type(statement)}')
        if isinstance(statement, ofxtools.models.bank.stmt.CCSTMTRS):
            print('Credit Card')
            b = statement.ccacctfrom
            print(f' AccountId: {b.acctid}')
        elif isinstance(statement, ofxtools.models.bank.stmt.STMTRS):
            b = statement.bankacctfrom
            print(f'    BankId: {b.bankid}')
            print(f' AccountId: {b.acctid}')
            print(f'AccoutType: {b.accttype}')
        else:
            print('I do not know that type yet')

        for txn in statement.transactions:
            # TXN: <STMTTRN(trntype='DIRECTDEP', dtposted=datetime.datetime(2023, 9, 28, 0, 0, tzinfo=<UTC>), trnamt=Decimal('3579.14'), fitid='1557162116', name='DIRECT DEP SHAPE SECURITY I ID91', memo='ACH, Deposit, Processed')>
            # TXN: <STMTTRN(trntype='FEE', dtposted=datetime.datetime(2023, 9, 15, 0, 0, tzinfo=<UTC>), trnamt=Decimal('-66.22'), fitid='6', name='LUCKY #757 SAN JOSE      SAN JO', memo='Fee, Processed')>
            print(f'TXN: {txn}')
    sys.exit()

