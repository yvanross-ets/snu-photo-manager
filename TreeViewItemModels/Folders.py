from kivy.app import App
from models.BaseModel import BaseModel
from models.PhotosTags import Folder

class Folders(BaseModel):
    name = 'Folders'

    def all(self):
        app = App.get_running_app()
        return app.session.query(Folder).order_by(Folder.name.asc()).all()



