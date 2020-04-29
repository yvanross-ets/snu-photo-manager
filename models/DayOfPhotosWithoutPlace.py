from kivy.app import App
from models.BaseModel import BaseModel
from models.PhotosTags import Photo

class DayOfPhotosWithoutPlace(BaseModel):
    photos = []

    def __init__(self,id,name,nb_photos):
        self.folder_id = id
        self.name = name
        self.nb_photos = nb_photos

    def photos(self):
        app = App.get_running_app()
        photos = app.session.query(Photo).filter(Photo.folder_id == self.folder_id).filter(Photo.place_id == None).order_by(Photo.original_date)
        return photos.all()




