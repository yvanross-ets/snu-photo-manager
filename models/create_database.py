
from models.Location import Location
from models.Face import Face
from models.FacePhoto import FacePhoto
from models.Person import Person
from models.PhotosTags import *

def create_database(engine):
    try:
        Face.create_table(engine)
        FacePhoto.create_table(engine)
        Location.create_table(engine)
        Person.create_table(engine)
        Folder.create_table(engine)
        Photo.create_table(engine)
        Tag.create_table(engine)

    except Exception as e:
        print(e)
        raise ValueError(e)



