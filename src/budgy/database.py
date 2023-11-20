from pathlib import Path

import ofxtools
from ofxtools.Parser import OFXTree

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update

Base = declarative_base()

class TransactionRecord(Base):
    __tablename__ = 'transactions'
    type = sqlalchemy.Column('type', sqlalchemy.String)
    posted = sqlalchemy.Column('posted', sqlalchemy.DateTime, primary_key=True, nullable=False)
    amount = sqlalchemy.Column('amount', sqlalchemy.Float, primary_key=True, nullable=False)
    fitid = sqlalchemy.Column('fitid', sqlalchemy.Integer, primary_key=True, nullable=False)
    name = sqlalchemy.Column('name', sqlalchemy.String, nullable=False)
    memo = sqlalchemy.Column('memo', sqlalchemy.String)
    checknum = sqlalchemy.Column('checknum', sqlalchemy.Integer)

class BudgyDatabase(object):
    MAX_COMMIT = 10000 # maximum number of records in single commit
    def __init__(self, path=None, echo=False):

        self.db_path = None
        self.db_engine = None
        if path is not None:
            self.open_database(path, echo=echo)

    def open_database(self, path, echo=False):
        self.db_path = path
        print(f'Opening DB: {self.db_path}')
        uri = f'sqlite:///{self.db_path}'
        print(uri)
        self.db_engine = sqlalchemy.create_engine(uri, echo = echo)
        self.metadata = Base.metadata # sqlalchemy.MetaData(self.db_engine)
        Base.metadata.create_all(self.db_engine)
        self.db_engine.connect()
        print('database open')
        return self.db_engine

    def _open_session(self):
        if not self.db_engine:
            return None
        Session = sessionmaker(bind = self.db_engine)
        return Session()

    def insert_records(self, records):
        with self._open_session() as session:
            session.execute(
                update(TransactionRecord),
                records
            )
            session.commit()
    def insert_records_orig(self, records, callback=None):
        with self._open_session() as session:
            count = 0
            for record in records:
                session.add(record)
                count += 1
                if count % self.MAX_COMMIT == 0:
                    print(f' - Committing {count} records...')
                    session.commit()
                    if callback:
                        callback(count)
            if count > 0:
                print(f' - Committing {count} records...')
                session.commit()
                if callback:
                    callback(count)

    def import_ofx_file(self, ofxfile:Path):
        parser = OFXTree()
        parser.parse(ofxfile)
        ofx = parser.convert()
        for statement in ofx.statements:
            is_checking = isinstance(statement, ofxtools.models.bank.stmt.STMTRS)
            records = []
            for txn in statement.transactions:
                checknum = txn.checknum if is_checking else None
                record = {
                    'type': txn.trntype,
                    'posted': txn.dtposted,
                    'amount': txn.trnamt,
                    'fitid': txn.fitid,
                    'name': txn.name,
                    'memo': txn.memo,
                    'checknum': checknum
                }
                records.append(record)
            self.insert_records(records)

