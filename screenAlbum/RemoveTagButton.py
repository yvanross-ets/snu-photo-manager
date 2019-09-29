from kivy.app import App

from generalElements.buttons.RemoveButton import RemoveButton
from generalElements.popups.NormalPopup import NormalPopup
from generalElements.popups.ConfirmPopup import ConfirmPopup


class RemoveTagButton(RemoveButton):
    """Button to remove a tag from the tags list.  Will popup a confirm dialog before removing."""

    def on_release(self):
        app = App.get_running_app()
        content = ConfirmPopup(text='Delete The Tag "'+self.to_remove+'"?', yes_text='Delete', no_text="Don't Delete", warn_yes=True)
        content.bind(on_answer=self.on_answer)
        self.owner.popup = NormalPopup(title='Confirm Delete', content=content, size_hint=(None, None), size=(app.popup_x, app.button_scale * 4), auto_dismiss=False)
        self.owner.popup.open()

    def on_answer(self, instance, answer):
        del instance
        if answer == 'yes':
            app = App.get_running_app()
            app.Tag.remove(self.to_remove)
            self.owner.update_treeview()
        self.owner.dismiss_popup()