from kivy.app import App
from kivy.properties import DictProperty, ObjectProperty, StringProperty

from generalcommands import naming
from generalElements.buttons.ExpandableButton import ExpandableButton
from screenImporting.ImportPresetArea import ImportPresetArea


class ImportPreset(ExpandableButton):
    data = DictProperty()
    owner = ObjectProperty()
    import_to = StringProperty('')

    def on_data(self, *_):
        import_preset = self.data
        naming_method = import_preset['naming_method']
        self.content = ImportPresetArea(index=self.index, title=import_preset['title'], import_to=import_preset['import_to'], naming_method=naming_method, naming_example=naming(naming_method), last_naming_method=naming_method, single_folder=import_preset['single_folder'], delete_originals=import_preset['delete_originals'], import_from=import_preset['import_from'], owner=self)

    def on_remove(self):
        app = App.get_running_app()
        app.import_preset_remove(self.index)
        self.owner.selected_import = -1
        self.owner.create_treeview()

    def on_release(self):
        self.owner.selected_import = self.index
        self.owner.import_preset()