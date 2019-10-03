from unittest import TestCase
import os
from models.FileInfo import FileInfo
from datetime import datetime



class TestFileInfo(TestCase):


  def test_photoInfo_original_date(self):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path,'..','photos')
    file_info= ['IMG0002.jpg',path]
    file_info = FileInfo(file_info)
    self.assertEqual(file_info.original_date, -1884010744.0)

    date_str = datetime.fromtimestamp(file_info.original_date).strftime('%Y:%m:%d %H:%M:%S')
    self.assertEqual(date_str,"1910:04:20 02:40:56")

  def test_load_gps(self):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path,'..','photos')
    file_info= ['IMG_gps.jpg',path]
    file_info = FileInfo(file_info)
    self.assertEqual(file_info.latitude, 45.444336111111106)
    self.assertEqual(file_info.longitude,-73.25209722222222)
    
  def test_new_folder_name(self):
    self.fail()

  def test_new_folder_with_filename(self):
    self.fail()

  def test_new_full_filename(self):
    self.fail()

  def test_old_full_filename(self):
    self.fail()
