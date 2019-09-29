from kivy.app import App

from generalElements.buttons.RemoveButton import RemoveButton


class RemoveFromTagButton(RemoveButton):
    """Button to remove a tag from the current photo."""

    def on_release(self):
        app = App.get_running_app()
        app.Tag.remove(self.remove_from, self.to_remove, message=True)
        self.owner.update_treeview()