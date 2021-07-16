from kivy.app import App
from TreeViewItem.TreeViewItem import TreeViewItem
from TreeViewItem.TreeViewItemTag import TreeViewItemTag
from generalElements.popups.InputPopupTag import InputPopupTag
from generalElements.popups.NormalPopup import NormalPopup
from models.PhotosTags import Tag


class TreeViewItemTags(TreeViewItem):
    indent = 0
    can_new_folder = True

    def visit(self, treeViewItem):
        super(TreeViewItemTags, self).visit()

        if self.expanded:
            treeViewItem.data = self.deleteChild(treeViewItem.data, self)
            self.expanded = False
        else:
            index = self.getItemIndex(treeViewItem.data, self)
            for tag in self.item.all():
                index += 1
                tag_item = TreeViewItemTag(self.owner, tag, self.height, self)
                treeViewItem.data.insert(index, tag_item)
            self.expanded = True

    def new_item(self,photoListRecyclerView):
        """Open new tag popup"""
        content = InputPopupTag(hint='Tag Name', text='Enter A Tag:')
        app = App.get_running_app()
        content.bind(on_answer=self.new_item_answer)
        self.photoListRecyclerView = photoListRecyclerView
        self.popup = NormalPopup(title='Create Tag', content=content, size_hint=(None, None),
                                 size=(app.popup_x, app.button_scale * 5), auto_dismiss=False)
        self.popup.open()


    def new_item_answer(self, instance=None, answer="yes"):
        """Adds the current input tag to the app tags."""

        if answer == "yes":
            if instance is not None:
                tag_name = instance.ids['input'].text.lower().strip(' ')
                if not tag_name:
                    self.dismiss_popup()
                    return
            else:
                tag_input = self.ids['newTag']
                tag_name = tag_input.text.lower().strip(' ')
                tag_input.text = ''

            tag = Tag(name=tag_name)
            app = App.get_running_app()
            app.session.add(tag)
            app.session.commit()
            self.popup.dismiss()

            # refresh tag treeview
            if self.expanded:
                self.visit(self.photoListRecyclerView)

            self.visit(self.photoListRecyclerView)



