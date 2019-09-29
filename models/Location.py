from models.Database import Database

class Location(Database):
  ID=0
  COUNTRY=1
  PROVINCE=2
  LOCALITY=3
  STREETNUMBER=4
  ROUTE=5
  POSTALCODE=6

  LOCATIONID=0
  PHOTOID=1

  def __init__(self,app,database):
    super(Location,self).__init__(app=app,database=database)
    self.__create()

  def __create(self):
    try:
      self.database.execute('select * from locations')
    except:
      self.database.execute('''CREATE TABLE IF NOT EXISTS locations(
                                      Id integer not null primary key autoincrement unique,
                                      Country text,
                                      Province text,
                                      Locality text,
                                      StreetNumber text,
                                      Route text,
                                      PostalCode text
                                      );''')

      self.database.execute('''CREATE TABLE IF NOT EXISTS locations_photos(
                                      LocationId integer not null,
                                      PhotoId integer not null);''')

      self.database.execute('''
          CREATE INDEX "location_Name" ON "locations" ("Country","Province","Locality","StreetNumber","Route","PostalCode");
        ''')

      self.database.execute('''
          CREATE INDEX "location_LocationId" ON "locations_photos" ("LocationId");
        ''')
      self.database.execute('''
          CREATE INDEX "location_PhotoId" ON "locations_photos" ("PhotoId");
        ''')
