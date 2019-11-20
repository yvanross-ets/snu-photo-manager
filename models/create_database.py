
from models.Face import Face
from models.FacePhoto import FacePhoto
from models.Person import Person
from models.PhotosTags import *
from models.places import *

def create_database(engine):
    try:
        Face.create_table(engine)
        FacePhoto.create_table(engine)

        Place.create_table(engine)
        Locality.create_table(engine)
        Province.create_table(engine)
        Country.create_table(engine)

        Person.create_table(engine)
        Folder.create_table(engine)
        Photo.create_table(engine)
        Tag.create_table(engine)

    except Exception as e:
        print(e)
        raise ValueError(e)



