from kivy.app import App
from models.BaseModel import BaseModel
from models.PhotosTags import Country
from TreeViewItem.TreeViewItem import TreeViewItem


class Countries(BaseModel):
    name = 'Countries'
    photos = []

    def countries(self):
        app = App.get_running_app()
        return app.session.query(Country).order_by(Country.name.asc()).all()


