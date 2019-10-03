from sqlalchemy import Column, Integer, String, Float,BLOB
from sqlalchemy import Sequence
from sqlalchemy.ext.declarative import declarative_base
from models.BaseModel import BaseModel
Base = declarative_base()


class FacePhoto(Base,BaseModel):
    __tablename__ = 'faces_photos'

    id = Column(Integer, Sequence('face_photo_id_seq'), primary_key=True)
    face__id = Column(Integer)
    photo_id = Column(Integer)

    def __repr__(self):
        return "<FacePhoto( id='%s', face_id='%d', photo_id='%d')>" % (
        self.id, self.face_id, self.photo_id)

    def create_table(engine):
        FacePhoto.__table__
        Base.metadata.create_all(engine)