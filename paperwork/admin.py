"""Настройки интерфейса администратора"""

from xml.etree import ElementTree
from typing import List

from django.contrib import admin

from . import models

MMISDB_NS = 'http://tempuri.org/dsMMISDB.xsd'
DIFFGR_NS = 'urn:schemas-microsoft-com:xml-diffgram-v1'


def get_subjects(filename: str) -> List[ElementTree]:
    """Загрузка предметы из файла *.plx"""

    root = ElementTree.parse(filename).getroot()
    plan = root.find(f'./{{{DIFFGR_NS}}}diffgram/{{{MMISDB_NS}}}dsMMISDB')
    subjects = plan.findall(f'./{{{MMISDB_NS}}}ПланыСтроки')
    return subjects


class EducationPlanAdmin(admin.ModelAdmin):
    """Администрирование учебных планов"""

    @admin.action(description="Импортировать дисциплины")
    def create_subjects(self, _request, queryset) -> None:
        """Импортировать дисциплины"""

        for edu_plan in queryset:
            if not edu_plan.file:
                continue
            subjects = get_subjects(edu_plan.file.path)
            for subject in subjects:
                print(subject)

    actions = [
        create_subjects
    ]

    list_display = [
        'code',
        'name',
        'degree',
        'short',
        'comment',
    ]


# class StudyGroupAdmin(admin.ModelAdmin):
#     """Администрирование учебных групп"""
#
#     list_display = [
#         'name',
#         'edu_plan',
#     ]


# admin.site.register(models.EducationPlan, EducationPlanAdmin)
# admin.site.register(models.StudyGroup, StudyGroupAdmin)
# admin.site.register(models.SubjectPlan)
# admin.site.register(models.Teacher)
# admin.site.register(models.TeacherSubject)
