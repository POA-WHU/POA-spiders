from dataclasses import dataclass
from pathlib import Path

project_path = Path(__file__).absolute().parent.parent


@dataclass
class Database:
    user = 'root'
    password = ''
    host = 'localhost'
    port = '3306'
    database = 'test_db'

    @property
    def server(self):
        return f'mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}'


@dataclass
class Log:
    format = '[%(name)-10s] %(levelname)-8s: %(message)s'
    level = 'DEBUG'


user_agents_path = project_path / 'src/base/utilities/user_agents.json'
