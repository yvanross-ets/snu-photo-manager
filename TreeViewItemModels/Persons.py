from kivy.app import App
from models.BaseModel import BaseModel
from models.Person import Person


class Persons(BaseModel):
    name = 'Persons'

    def all(self):
        app = App.get_running_app()
        return app.session.query(Person).order_by(Person.first_name.asc()).all()


