from kivy.app import App

from generalElements.RemoveButton import RemoveButton


class RemoveFromTagButton(RemoveButton):
    """Button to remove a tag from the current photo."""

    def on_release(self):
        app = App.get_running_app()
        app.database_remove_tag(self.remove_from, self.to_remove, message=True)
        self.owner.update_treeview()