from unittest import TestCase
from utils.StringEx import *

class TestCreation_date_from_full_filename(TestCase):
    def test_creation_date_from_full_filename(self):
        str = "user/1850/05/03/allomoncoco.jpg"
        result = creation_date_from_full_filename(str)
        self.assertEqual(result, -3776179348.999001)

        str = "user/1850-05-03/allomoncoco.jpg"
        result = creation_date_from_full_filename(str)
        self.assertEqual(result, -3776179348.999001)

        str = 'user\\1850\\05\\03\\allomoncoco.jpg'
        result = creation_date_from_full_filename(str)
        self.assertEqual(result, -3776179348.999001)

        str = "user/1850-05/allomoncoco.jpg"
        result = creation_date_from_full_filename(str)
        self.assertEqual(result,None)
