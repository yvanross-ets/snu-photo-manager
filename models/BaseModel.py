from kivy.app import App

class BaseModel:

    def can_delete(self):
        return False

    def delete(self):
        if self.can_delete():
            app = App.get_running_app()
            app.session.delete(self)
            app.session.commit()

    def dict(self):
        ret = {}
        for attr in dir(self):
            if not attr.startswith('__'):
                ret[attr] = getattr(self, attr)
        return ret

