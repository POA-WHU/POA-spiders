from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError, OperationalError, DataError
from sqlalchemy.orm import sessionmaker

from ..logger import Logger
from .models import *


class DBHandler:
    def __init__(self, server: str, database: str):
        self._logger = Logger(self.__class__.__name__)
        engine = create_engine(server)
        try:
            engine.execute(f'CREATE DATABASE {database}')
            self._logger.warning(f'no existing database called {database}, a new one has been created')
        except ProgrammingError:
            pass
        engine.execute(f'USE {database}')
        self._Session = sessionmaker(bind=engine)
        try:
            Base.metadata.create_all(engine)
        except OperationalError:
            pass

    def insert(self, atc: Article):
        self._logger.debug(f'trying to insert new article: {atc}')
        session = self._Session()
        try:
            session.add(atc)
            session.commit()
        except DataError:
            self._logger.error('data error', exc_info=True)
        self._logger.debug(f'insertion finished successfully')
