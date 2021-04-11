from pathlib import Path

project_path = Path(__file__).absolute().parent.parent


class Database:
    user = 'root'
    password = ''
    host = 'localhost'
    port = '3306'
    database = 'test_db'

    server = f'mysql+pymysql://{user}:{password}@{host}:{port}'



class Log:
    format = '[%(name)-10s] %(levelname)-8s: %(message)s'
    level = 'DEBUG'


user_agents_path = project_path / 'src/base/utilities/user_agents.json'
temp_pdf_path = project_path / 'src/temp.pdf'
