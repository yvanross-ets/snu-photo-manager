from kivy.app import App
from models.BaseModel import BaseModel
from TreeViewItem.TreeViewItem import TreeViewItem
from models.Face import Face

class Faces(BaseModel):
    name = 'Faces'

    def all(self):
        app = App.get_running_app()
        return app.session.query(Face).order_by(Face.id.asc()).all()


