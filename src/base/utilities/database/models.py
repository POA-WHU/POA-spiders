from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, TEXT, DATE, LONGTEXT

Base = declarative_base()


class Article(Base):
    __tablename__ = 'articles'

    id = Column(INTEGER, primary_key=True)
    publisher = Column(VARCHAR(16), nullable=False)
    url = Column(TEXT, nullable=False)
    title = Column(TEXT, nullable=False)
    date = Column(DATE, nullable=False)
    content = Column(LONGTEXT, nullable=False)
    authors = Column(TEXT)
    abstract = Column(TEXT)
    location = Column(TEXT)
    section = Column(VARCHAR(32))
    category = Column(TEXT)
    pic_url = Column(TEXT)
    type = Column(VARCHAR(32))

    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title}')>"
