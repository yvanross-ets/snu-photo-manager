from models.Database import Database

class Face(Database):
  ID=0
  PHOTOID=1
  LEFT=2
  RIGHT=3
  TOP=4
  BOTTOM=5
  THUMBNAIL=6

  def __init__(self,app, database):
    print("Face init")
    print(app)
    print(database)
    super(Face,self).__init__(app=app, database=database)
    self.__create()

  def __create(self):
    try:
      self.database.execute('select * from faces')
    except:
      self.database.execute('''CREATE TABLE IF NOT EXISTS faces(
                                      Id integer not null primary key autoincrement unique,
                                      PhotoId integer not null,
                                      Left integer not null,
                                      Right integer not null,
                                      Top integer not null,
                                      Bottom integer not null,
                                      face blob);''')

      self.database.execute('''
          CREATE INDEX "face_photo_id" ON "faces" ("PhotoId");
        ''')
