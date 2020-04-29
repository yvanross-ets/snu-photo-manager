from kivy.app import App
from models.BaseModel import BaseModel
from models.PhotosTags import Tag

class Tags(BaseModel):
    name = 'Tags'
    can_new_folder = True

    def all(self):
        app = App.get_running_app()
        return app.session.query(Tag).filter(Tag.name != 'Favorites').order_by(Tag.name.asc()).all()