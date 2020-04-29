from kivy.app import App
from models.BaseModel import BaseModel
from models.PhotosTags import Photo

class Videos(BaseModel):
    name = 'Videos'

    def all(self):
        app = App.get_running_app()
        return app.session.query(Photo).all()


