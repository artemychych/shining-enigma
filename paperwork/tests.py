"""Тестирование Paperwork"""

from django.test import TestCase

from .models import EducationPlan


class TestModelEducationPlan(TestCase):
    def test_str(self):
        code = "09.03.01"
        name = "Информатика и вычислительная техника"
        short = "ИВТ"
        comment = "2020 год поступления"

        m = EducationPlan()
        m.code = code
        m.name = name
        self.assertEqual(str(m), f"{code} {name}")
        m.comment = comment
        self.assertEqual(str(m), f"{code} {name} ({comment})")

        m.short = short
        self.assertEqual(str(m), f"{code} {short} ({comment})")
        m.comment = ""
        self.assertEqual(str(m), f"{code} {short}")


class TestModelSubjectPlan(TestCase):
    def test_str(self):
        code = "09.03.01"
        name = "Информатика и вычислительная техника"

        m = EducationPlan()
        m.code = code
        m.name = name
        self.assertEqual(str(m), f"{code} {name}")


class TestViews(TestCase):
    def test_index_page(self):
        self.assertTemplateUsed('paperwork/index.html')
