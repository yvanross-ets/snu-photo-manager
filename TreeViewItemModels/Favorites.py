from kivy.app import App
from models.BaseModel import BaseModel
from models.PhotosTags import Tag


class Favorites(BaseModel):
    name = 'Favorites'

    def favorites(self):
        app = App.get_running_app()
        tag = app.session.query(Tag).filter_by(name="Favorites").first()
        if tag is  None:
             tag = Tag(name='Favorites')
             app.session.add(tag)
             app.session.commit()
        return tag.photos


