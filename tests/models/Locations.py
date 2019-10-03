import os
import sqlite3

from unittest import TestCase

from models.Location import Location


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
    def test_sqlalchemy(self):

        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import create_engine
        engine = create_engine('sqlite:///gomp_test.db', echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()

        location = Location(country="canada", province="Québec",locality="Montreal", street_number="1100", route="Notre-Dame ouest", postal_code="H13 k45" )
        print(location)
        session.add(location)
        dirty = session.dirty
        sn = session.new

        location2 = Location(country="canada2", province="Québec2", locality="Montreal2", street_number="11002",
                            route="Notre-Dame ouest2", postal_code="H13 k42")
        print(location2)
        session.add(location2)


        our_location = session.query(Location).filter_by(country='canada').first()
        session.commit()
        print(location)
        print(location2)
        print(our_location)

        pass

