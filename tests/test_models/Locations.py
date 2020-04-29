import os
import sqlite3

from unittest import TestCase



class TestFileInfo(TestCase):

    # def test_insert_location(self):
    #     dir_path = os.path.dirname(os.path.realpath(__file__))
    #     database_path = os.path.join(dir_path, "location_test_db")
    #     os.remove(database_path)
    #     database = sqlite3.connect(database_path)
    #     location = Location(database)
    #
    #     id = location.insert_or_find_location("Canada1", "Québec", "Montréal", "1100", "Rue Notre-Dame Ouest", "H3C1K3")
    #     self.assertEqual(1,id)
    #
    #     id = location.insert_or_find_location("Canada1", "Québec", "Montréal", "1100","Rue Notre-Dame Ouest", "H3C1K3")
    #     self.assertEqual(1, id)
    #
    #     id = location.insert_or_find_location("Canada2", "Québec", "Montréal", "1100", "Rue Notre-Dame Ouest", "H3C1K3")
    #     self.assertEqual(2, id)
    #
    #     res = location.insert_location_photo(1, 1)
    #
    #     res = location.insert_location_photo(1, 1)
    #     res = location.insert_location_photo(1, 2)
    #     res = location.insert_location_photo(1, 3)
    #     res = location.insert_location_photo(2, 4)
    #
    #     res = location.delete_location_photo(1, 2)
    #
    #     res = location.delete(1)
    #
    #
    #     res = location.get_photos(1)
    #
    #     res = location.get_photos(2)



    ## https://docs.sqlalchemy.org/en/13/orm/tutorial.html
    # def test_sqlalchemy(self):
    #
    #     from sqlalchemy.orm import sessionmaker
    #     from sqlalchemy import create_engine
    #     from models.PhotosTags import Country
    #     engine = create_engine('sqlite:///gomp_test.db', echo=True)
    #     Session = sessionmaker(bind=engine)
    #     session = Session()
    #
    #     location = Country(id="123",name="canada")
    #     print(location)
    #     session.add(location)
    #     print("added")
    #     dirty = session.dirty
    #     print(dirty)
    #     sn = session.new
    #     print(sn)
    #
    #     pass


    pass
