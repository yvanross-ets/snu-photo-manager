from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

from kivy.lang.builder import Builder
Builder.load_string("""
<ScreenDatabaseRestore>:
    BoxLayout:
        orientation: 'vertical'
        MainHeader:
        MainArea:
            orientation: 'vertical'
            Widget:
            NormalLabel:
                text: 'Restoring screenDatabase backup, please wait...'
            Widget:

""")


class ScreenDatabaseRestore(Screen):
    popup = None

    def dismiss_extra(self):
        """Dummy function, not valid for this screen, but the app calls it when escape is pressed."""
        return True

    def on_enter(self):
        app = App.get_running_app()
        completed = app.database_restore_process()
        if completed != True:
            app.message("Error: "+completed)
        app.setup_database(restore=True)
        Clock.schedule_once(app.show_database, 1)