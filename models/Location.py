from sqlalchemy import Column, Integer, String, Float
from sqlalchemy import Sequence
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, Sequence('location_id_seq'),primary_key=True)
    country = Column(String)
    province = Column(String)
    locality = Column(String)
    street_number = Column(String)
    route = Column(String)
    postal_code = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    gps_radius = Column(Float)
    nb_photos = Column(Integer)
    description = Column(String)


    def __repr__(self):
        return "<Location( id='%s',country='%s', province='%s', locality='%s', street_number='%s', route='%s', postal_code='%s')>" % (
                                self.id,self.country, self.province, self.locality,self.street_number, self.route, self.postal_code)
#
# def __init__(self,database):
#     super(Location,self).__init__(database=database)
#     self.__create()
#
#
# def insert_or_find_location(self, country, province, locality, street_number, route, postal_code):
#     locations = list(self.database.execute("select * from locations where Country =? AND Province=? AND Locality=? AND StreetNumber=? AND Route=? AND PostalCode=?",(country, province, locality, street_number, route, postal_code)))
#     if locations:
#         location_id = locations[0][Location.ID]
#     else:
#         res = self.database.execute("insert into locations(Country, Province, Locality, StreetNumber, Route, PostalCode) values(?, ?,?, ?, ?, ?)", (country, province, locality, street_number, route, postal_code))
#         res2 = self.commit()
#         location_id = res.lastrowid
#     return location_id
#
# def insert_location_photo(self,location_id, photo_id):
#     res = self.database.execute('insert into locations_photos(locationId,PhotoId) values(?,?)', (location_id, photo_id))
#     self.commit()
#     return res.lastrowid
#
# def delete_location_photo(self, location_id, photo_id):
#     res = self.database.execute('delete from locations_photos where LocationId = location_id and photoID = photo_id', (location_id, photo_id))
#     self.commit()
#     return res.lastrowid
#
# def get_photos(self,location_id):
#     photos = list(self.database.execute('select PhotoId from location_photos where locationId = ?',location_id))
#     return photos
#
# def delete(self,location_id):
#     res = self.database.execute('delete from locations where id = ?',location_id)
#     res2 = self.database.execute('delete from locations_photos where locationId = location_id')
#     self.commit()
#     return self.database
#
# def __create(self):
#     try:
#         self.database.execute('select * from locations')
#     except:
#         self.database.execute('''CREATE TABLE IF NOT EXISTS locations(
#                                       Id integer not null primary key autoincrement unique,
#                                       Country text,
#                                       Province text,
#                                       Locality text,
#                                       StreetNumber text,
#                                       Route text,
#                                       PostalCode text
#                                       );''')
#
#         self.database.execute('''CREATE TABLE IF NOT EXISTS locations_photos(
#                                       LocationId integer not null,
#                                       PhotoId integer not null);''')
#
#         self.database.execute('''
#           CREATE unique INDEX "location_Name" ON "locations" ("Country","Province","Locality","StreetNumber","Route","PostalCode");
#         ''')
#
#         self.database.execute('''
#           CREATE unique INDEX "location_photo" ON "locations_photos" ("LocationId","PhotoId");
#         ''')
#
#         self.database.execute('''
#           CREATE INDEX "location_LocationId" ON "locations_photos" ("LocationId");
#         ''')
#         self.database.execute('''
#           CREATE INDEX "location_PhotoId" ON "locations_photos" ("PhotoId");
#         ''')

# # engine = create_engine('sqlite:///:memory:', echo=True)
    def create_table(engine):
        Location.__table__
        Base.metadata.create_all(engine)