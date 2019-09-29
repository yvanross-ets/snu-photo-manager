from kivy.properties import  ObjectProperty


class Database():
  database = None
  app = None

  def __init__(self, app, database):
    print("xxxx")
    print(app)
    print(database)
    self.database = database
    self.app = app

  def close(self):
    self.database.close()
    return self.database

  def join(self):
    self.database.join()
    return self.database

  def commit(self):
    self.database.commit()
    return self.database
