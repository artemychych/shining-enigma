"""Модели данных"""

from django.db import models

# Уровень квалификации
# DEGREES = (
#     ('B', "Бакалавриат"),
#     ('M', "Магистратура"),
#     ('S', "Специалитет"),
# )

# MMISDB_NS = 'http://tempuri.org/dsMMISDB.xsd'
# DIFFGR_NS = 'urn:schemas-microsoft-com:xml-diffgram-v1'
# NAMESPACES = {
#     'msdata': 'urn:schemas-microsoft-com:xml-msdata',
# }


# class EducationPlan(models.Model):
#     """Учебный план"""
#
#     code = models.CharField(
#         verbose_name="код специальности",
#         max_length=20,
#     )
#     name = models.CharField(
#         verbose_name="название специальности",
#         max_length=75,
#     )
#     degree = models.CharField(
#         verbose_name="уровень квалификации",
#         max_length=1,
#         choices=DEGREES,
#     )
#     short = models.CharField(
#         verbose_name="сокращение",
#         max_length=10,
#         blank=True,
#         default='',
#     )
#     comment = models.CharField(
#         verbose_name="примечание",
#         max_length=100,
#         blank=True,
#         default='',
#     )
#     file = models.FileField(
#         upload_to='edu_plans',
#         verbose_name="файл",
#         blank=True,
#     )
#
#     class Meta:
#         verbose_name = "учебный план"
#         verbose_name_plural = "учебные планы"
#         ordering = ['code', 'name', 'degree']
#
#     def __str__(self):
#         if self.short:
#             result = f'{self.code} {self.short}'
#         else:
#             result = f'{self.code} {self.name}'
#         if self.comment:
#             result = f'{result} ({self.comment})'
#         return result


# class StudyGroup(models.Model):
#     """Учебная группа"""
#
#     name = models.CharField(
#         verbose_name="название",
#         max_length=20,
#     )
#     year = models.IntegerField(
#         verbose_name="год поступления",
#     )
#     edu_plan = models.ForeignKey(
#         to='EducationPlan',
#         on_delete=models.CASCADE,
#         verbose_name="учебный план",
#     )
#
#     class Meta:
#         verbose_name = "учебная группа"
#         verbose_name_plural = "учебные группы"
#
#     def __str__(self):
#         return f'{self.name}'


# class SubjectPlan(models.Model):
#     """Рабочая программа дисциплины"""
#
#     study_group = models.ForeignKey(
#         to='EducationPlan',
#         on_delete=models.CASCADE,
#         verbose_name="учебный план",
#     )
#     code = models.CharField(
#         verbose_name="код",
#         max_length=15,
#     )
#     name = models.CharField(
#         verbose_name="название",
#         max_length=75,
#     )
#     file = models.FileField(
#         upload_to='subj_plans',
#         verbose_name="файл",
#         blank=True,
#     )
#
#     class Meta:
#         verbose_name = "рабочая программа дисциплины"
#         verbose_name_plural = "рабочие программы дисциплин"
#
#     def __str__(self):
#         return f'{self.code} {self.name}'


# class Teacher(models.Model):
#     """Преподаватель"""
#
#     name = models.CharField(
#         verbose_name="ФИО",
#         max_length=75,
#     )
#
#     class Meta:
#         verbose_name = "преподаватель"
#         verbose_name_plural = "преподаватели"
#
#     def __str__(self):
#         return f'{self.name}'


# class TeacherSubject(models.Model):
#     """Дисциплины преподавателя"""
#
#     teacher = models.ForeignKey(
#         to='Teacher',
#         on_delete=models.CASCADE,
#         verbose_name="преподаватель",
#     )
#     study_group = models.ForeignKey(
#         to='StudyGroup',
#         on_delete=models.CASCADE,
#         verbose_name="учебная группа",
#     )
#
#     class Meta:
#         verbose_name = "дисциплина преподавателя"
#         verbose_name_plural = "дисциплины преподавателя"
