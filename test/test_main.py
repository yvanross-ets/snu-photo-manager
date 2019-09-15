#import unittest
from kivy.app import App
from main import PhotoManager

def fun(x):
    return x + 1


def test_answer():
  assert fun(3) == 4


def test_answer2():
  assert fun(3) == 4

def test_main():
  photomanager= PhotoManager()
  #photomanager.set_single_database()
  #print("allo mon coco")
  #print(photomanager)
  assert True



