from base.utilities.database import DBHandler
from base.utilities.functions import pdf2text
from config import Database


class PDFTransformer:
    def __init__(self) -> None:
        self.db_handler = DBHandler(Database.server, Database.database)
    
    def run(self) -> None:
        gen = self.db_handler.transform_all_pdf()
        pdf_urls = next(gen)
        texts = []
        for i in pdf_urls:
            texts.append(pdf2text(i))
        try:
            gen.send(texts)
        except StopIteration:
            pass


if __name__ == '__main__':
    PDFTransformer().run()
