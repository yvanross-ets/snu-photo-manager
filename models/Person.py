import os

from models.Database import Database


class Person(Database):
  ID = 0
  NAME = 1

  FACEID = 0
  PHOTOID = 1

  def __init__(self, app, database):
    super(Person,self).__init__(app=app,database=database)
    self.__create()

  def all(self):
    return list(self.database.execute('SELECT * FROM persons order by name'))

  def create(self, person_name):
    """Create a new person .
    Argument:
        person_name: String, name of the tag to create.
    """
    self.database.execute("insert into persons values(?)", (person_name))
    self.commit()

  def remove(self, person_name):
    """Deletes a person.
    Argument:
        person: String, the person to be deleted."""

    person = person_name.lower()
    person_file = os.path.join(self.person_directory, person + '.person')
    if os.path.isfile(person_file):
      os.remove(person_file)
    if person in self.persons:
      self.persons.remove(person)
    self.message("Deleted the person '" + person + "'")

  def photos(self, person):
    """Gets all photos that have a person applied to them.
    Argument:
        person: String, the person to search for.
    Returns:
        List of photoinfo Lists.
    """
    raise ValueError('fix Person photos')
    # person = person.lower()
    # match = '%' + person + '%'
    # photos = list(self.photos.select('SELECT * FROM photos WHERE Persons LIKE ?', (match,)))
    # checked_photos = []
    # for photo in photos:
    #     persons = photo[14].split(',')
    #     if person in persons:
    #         checked_photos.append(photo)
    # return local_paths(checked_photos)

  def add(self, fullpath, person):
    """Adds a person to a photo.
    Arguments:
        fullpath: String, the screenDatabase-relative path to the photo.
        person: String, the person to be added.
    """

    raise ValueError('Person add must fix')
    # person = person.lower().strip(' ')
    # fullpath = agnostic_path(fullpath)
    # info = self.photos.select('SELECT * FROM photos WHERE FullPath = ?', (fullpath, ))
    # info = list(info)
    # if info:
    #     info = list(info[0])
    #     original_persons = info[14].split(',')
    #     current_persons = []
    #     update = False
    #     for original in original_persons:
    #         if original.strip(' '):
    #             current_persons.append(original)
    #         else:
    #             update = True
    #     if person not in current_persons:
    #         current_persons.append(person)
    #         update = True
    #     if update:
    #         new_persons = ",".join(current_persons)
    #         info[14] = new_persons
    #         self.app.Photo.update(info)
    #         self.update_photoinfo(folders=info[1])
    #         return True
    return False


  def remove(self, fullpath, person, message=False):
    raise ValueError("must fix remove")
    # person = person.lower()
    # fullpath = agnostic_path(fullpath)
    # info = self.photos.select('SELECT * FROM photos WHERE FullPath = ?', (fullpath,))
    # info = list(info)
    # if info:
    #   info = list(info[0])
    #   current_persons = info[14].split(',')
    #   if person in current_persons:
    #     current_persons.remove(person)
    #     new_tags = ",".join(current_persons)
    #     info[14] = new_tags
    #     self.Photo.update(info)
    #     self.update_photoinfo(folders=info[1])
    #     if message:
    #       self.message("Removed person '" + person + "' from the photo.")


  def __create(self):
    try:
      self.database.execute('select * from persons')
    except:
      self.database.execute('''CREATE TABLE IF NOT EXISTS persons(
                                        Id integer not null primary key autoincrement unique,
                                        Name text);''')

      self.database.execute('''CREATE TABLE IF NOT EXISTS faces_persons(
                                        FaceId integer not null,
                                        PhotoId integer not null);''')

      self.database.execute('''
          CREATE INDEX "person_Name" ON "persons" ("Name");
        ''')
      self.database.execute('''
          CREATE INDEX "person_FaceId" ON "faces_persons" ("FaceId");
        ''')
      self.database.execute('''
          CREATE INDEX "person_PhotoId" ON "faces_persons" ("PhotoId");
        ''')
