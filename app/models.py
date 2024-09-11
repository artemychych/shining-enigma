from os.path import join
from xml.etree import ElementTree

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

MMISDB_NS = 'http://tempuri.org/dsMMISDB.xsd'
DIFFGR_NS = 'urn:schemas-microsoft-com:xml-diffgram-v1'

db = SQLAlchemy()


class EduPlan(db.Model):
    """Учебный план"""
    pk: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(75))
    degree: Mapped[str] = mapped_column(String(1))
    short: Mapped[str] = mapped_column(String(10))
    comment: Mapped[str] = mapped_column(String(100))
    file: Mapped[str] = mapped_column(String(255))

    def __str__(self) -> str:
        """Представление объекта"""
        result = self.code
        result += ' ' + self.short if self.short else self.name
        if self.comment:
            result += ' (' + self.comment + ')'
        return result

    @classmethod
    def load(cls, filename: str, plan: bytes) -> None:
        filepath = join('app', 'edu_plans', filename)
        with open(filepath, mode='wb') as file:
            file.write(plan)

        root = ElementTree.parse(filepath).getroot()
        plan1 = root.find(f'./{{{DIFFGR_NS}}}diffgram')
        plan2 = plan1.find(f'./{{{MMISDB_NS}}}dsMMISDB')
        plan3 = plan2.find(f'./{{{MMISDB_NS}}}ООП')

        obj = cls()
        obj.code = plan3.attrib['Шифр']
        obj.name = plan3.attrib['Название']
        obj.degree = plan3.attrib['УровеньОбразования']
        obj.short = ''
        obj.comment = ''
        obj.file = filename

        db.session.add(obj)
        db.session.commit()
