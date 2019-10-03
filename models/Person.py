from sqlalchemy import Column, Integer, String
from sqlalchemy import Sequence
from sqlalchemy.ext.declarative import declarative_base
from models.BaseModel import BaseModel
Base = declarative_base()


class Person(Base,BaseModel):
    __tablename__ = 'persons'

    id = Column(Integer, Sequence('person_id_seq'), primary_key=True)
    uuid = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    name = 'Person Name'

    def __repr__(self):
        return "<Person( id='%s',uuid='%s', first_name='%s', last_name='%s', email='%s')>" % (
            self.id, self.uuid, self.first_name, self.last_name, self.email)

    # def all(self):
    #   return list(self.database.execute('SELECT * FROM persons order by name'))
    #
    # def create(self, person_name):
    #   """Create a new person .
    #   Argument:
    #       person_name: String, name of the tag to create.
    #   """
    #   self.database.execute("insert into persons values(?)", (person_name))
    #   self.commit()
    #
    # def remove(self, person_name):
    #   """Deletes a person.
    #   Argument:
    #       person: String, the person to be deleted."""
    #
    #   person = person_name.lower()
    #   person_file = os.path.join(self.person_directory, person + '.person')
    #   if os.path.isfile(person_file):
    #     os.remove(person_file)
    #   if person in self.persons:
    #     self.persons.remove(person)
    #   self.message("Deleted the person '" + person + "'")
    #
    # def photos(self, person):
    #   """Gets all photos that have a person applied to them.
    #   Argument:
    #       person: String, the person to search for.
    #   Returns:
    #       List of photoinfo Lists.
    #   """
    #   raise ValueError('fix Person photos')
    #   # person = person.lower()
    #   # match = '%' + person + '%'
    #   # photos = list(self.photos.select('SELECT * FROM photos WHERE Persons LIKE ?', (match,)))
    #   # checked_photos = []
    #   # for photo in photos:
    #   #     persons = photo[14].split(',')
    #   #     if person in persons:
    #   #         checked_photos.append(photo)
    #   # return local_paths(checked_photos)
    #
    # def add(self, fullpath, person):
    #   """Adds a person to a photo.
    #   Arguments:
    #       fullpath: String, the screenDatabase-relative path to the photo.
    #       person: String, the person to be added.
    #   """
    #
    #   raise ValueError('Person add must fix')
    #   # person = person.lower().strip(' ')
    #   # fullpath = agnostic_path(fullpath)
    #   # info = self.photos.select('SELECT * FROM photos WHERE FullPath = ?', (fullpath, ))
    #   # info = list(info)
    #   # if info:
    #   #     info = list(info[0])
    #   #     original_persons = info[14].split(',')
    #   #     current_persons = []
    #   #     update = False
    #   #     for original in original_persons:
    #   #         if original.strip(' '):
    #   #             current_persons.append(original)
    #   #         else:
    #   #             update = True
    #   #     if person not in current_persons:
    #   #         current_persons.append(person)
    #   #         update = True
    #   #     if update:
    #   #         new_persons = ",".join(current_persons)
    #   #         info[14] = new_persons
    #   #         self.app.Photo.update(info)
    #   #         self.update_photoinfo(folders=info[1])
    #   #         return True
    #   return False
    #
    #
    # def remove(self, fullpath, person, message=False):
    #   raise ValueError("must fix remove")
    #   # person = person.lower()
    #   # fullpath = agnostic_path(fullpath)
    #   # info = self.photos.select('SELECT * FROM photos WHERE FullPath = ?', (fullpath,))
    #   # info = list(info)
    #   # if info:
    #   #   info = list(info[0])
    #   #   current_persons = info[14].split(',')
    #   #   if person in current_persons:
    #   #     current_persons.remove(person)
    #   #     new_tags = ",".join(current_persons)
    #   #     info[14] = new_tags
    #   #     self.Photo.update(info)
    #   #     self.update_photoinfo(folders=info[1])
    #   #     if message:
    #   #       self.message("Removed person '" + person + "' from the photo.")

    def create_table(engine):
        Person.__table__
        Base.metadata.create_all(engine)