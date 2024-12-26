from app.extensions import db
from datetime import datetime
import yaml
from sqlalchemy.orm import mapped_column
from sqlalchemy.types import String
from xml.etree import ElementTree
from os.path import join

MMISDB_NS = 'http://tempuri.org/dsMMISDB.xsd'
DIFFGR_NS = 'urn:schemas-microsoft-com:xml-diffgram-v1'

class EduPlan(db.Model):
    """Учебный план"""
    pk = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(75))
    degree = db.Column(db.String(1))
    short = db.Column(db.String(10))
    comment = db.Column(db.String(100))
    file = db.Column(db.String(255))

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
        plan2 = plan1.find(f'./{{{MMISDB_NS}}}dsMMISDB') # type: ignore
        plan3 = plan2.find(f'./{{{MMISDB_NS}}}ООП') # type: ignore

        obj = cls()
        obj.code = plan3.attrib['Шифр'] # type: ignore
        obj.name = plan3.attrib['Название'] # type: ignore
        obj.degree = plan3.attrib['УровеньОбразования'] # type: ignore
        obj.short = ''
        obj.comment = ''
        obj.file = filename

        db.session.add(obj)
        db.session.commit()
        
class YamlFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<YamlFile {self.name}>'
    
class YamlDocument(db.Model):
    """Модель для хранения YAML документов"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def validate_yaml(content: str) -> bool:
        """Проверка валидности YAML"""
        try:
            yaml.safe_load(content)
            return True
        except yaml.YAMLError:
            return False

class DocxFile(db.Model):
    """Модель для хранения сгенерированных DOCX файлов"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    edu_plan_id = db.Column(db.Integer, db.ForeignKey('edu_plan.pk'))
    yaml_doc_id = db.Column(db.Integer, db.ForeignKey('yaml_document.id'))
    
    edu_plan = db.relationship('EduPlan', backref='docx_files')
    yaml_doc = db.relationship('YamlDocument', backref='docx_files')

    def __str__(self):
        return self.name