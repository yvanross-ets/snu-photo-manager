from kivy.app import App
from TreeViewItem.TreeViewItem import TreeViewItem
from generalElements.popups.InputPopup import InputPopup
from generalElements.popups.NormalPopup import NormalPopup
from generalElements.popups.ConfirmPopup import ConfirmPopup

class TreeViewItemTag(TreeViewItem):
    indent = 1
    can_rename_folder = True
    can_delete_folder = True


    def visit(self,screenDatabase):
        super(TreeViewItemTag, self).visit()

        screenDatabase = self.owner
        datas = []
        for photo in self.item.photos:
            datas.append(photo.data_item(screenDatabase))

        screenDatabase.data = datas
        screenDatabase.update_can_browse()
        screenDatabase.update_selected()

    def visit_drop(self,visitors):
        self.owner.add_to_tag(self.item,visitors)
        self.target = 'allo'


    def rename_item(self,photoListRecyclerView):
        """Starts the folder renaming process, creates an input text popup."""

        content = InputPopup(hint=self.item.name, text='Rename To:')
        app = App.get_running_app()
        self.photoListRecyclerView = photoListRecyclerView
        content.bind(on_answer=self.rename_item_answer)
        self.photoListRecyclerView = photoListRecyclerView
        self.popup = NormalPopup(title='Rename Tag', content=content, size_hint=(None, None),
                                 size=(app.popup_x, app.button_scale * 5), auto_dismiss=False)
        self.popup.open()

    def rename_item_answer(self, instance, answer):
        """Tells the app to rename the folder if the dialog is confirmed.
        Arguments:
            instance: The dialog that called this function.
            answer: String, if 'yes', the folder will be renamed, all other answers will just close the dialog.
        """

        if answer == 'yes':
            text = instance.ids['input'].text.strip(' ')
            app = App.get_running_app()
            self.item.name =text
            app.session.commit()

        self.popup.dismiss()
        self.__refresh_tree_view()


    def delete_item(self,photoListRecyclerView):
        """Starts the delete folder process, creates the confirmation popup."""


        text = "Delete tag "+ self.item.name + "\nThe Contained Files Will Not Be Deleted."
        content = ConfirmPopup(text=text, yes_text='Delete', no_text="Don't Delete", warn_yes=True)
        app = App.get_running_app()
        self.photoListRecyclerView = photoListRecyclerView
        content.bind(on_answer=self.delete_item_answer)
        self.popup = NormalPopup(title='Confirm Delete', content=content, size_hint=(None, None),
                                 size=(app.popup_x, app.button_scale * 4), auto_dismiss=False)
        self.popup.open()

    def delete_item_answer(self, instance, answer):
        """Tells the app to delete the folder if the dialog is confirmed.
        Arguments:
            instance: The dialog that called this function.
            answer: String, if 'yes', the folder will be deleted, all other answers will just close the dialog.
        """
        del instance
        if answer == 'yes':
            self.item.delete()
            #self.previous_album()
        self.popup.dismiss()
        self.__refresh_tree_view()


    def __refresh_tree_view(self):
        if self.treeViewItemParent.expanded:
            self.treeViewItemParent.visit(self.photoListRecyclerView)

        self.treeViewItemParent.visit(self.photoListRecyclerView)
