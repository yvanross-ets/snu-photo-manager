from sqlalchemy import Column, Integer,BLOB
from sqlalchemy import Sequence
from sqlalchemy.ext.declarative import declarative_base
from models.BaseModel import BaseModel
Base = declarative_base()


class Face(Base,BaseModel):
  __tablename__ = 'faces'

  id = Column(Integer, Sequence('face_id_seq'), primary_key=True)
  photo_id = Column(Integer)
  left = Column(Integer)
  right = Column(Integer)
  top = Column(Integer)
  bottom = Column(Integer)
  face = Column(BLOB)
  name = 'Face'

  def __repr__(self):
    return "<Face( id='%s',left='%f', right='%f', top='%f', bottom='%f')>" % (
      self.id, self.left, self.right, self.top, self.bottom)

  def create_table(engine):
    Face.__table__
    Base.metadata.create_all(engine)