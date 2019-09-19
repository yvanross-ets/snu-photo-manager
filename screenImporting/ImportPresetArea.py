from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout

from filebrowser import FileBrowser
from generalcommands import local_path, naming
from generalElements.MenuButton import MenuButton
from generalElements.NormalDropDown import NormalDropDown
from generalElements.NormalPopup import NormalPopup
from screenImporting.ImportPresetForlder import ImportPresetFolder

from kivy.lang.builder import Builder

Builder.load_string("""
<ImportPresetArea>:
    cols: 1 if app.simple_interface else 2
    size_hint_y: None
    padding: app.padding
    spacing: app.padding, 0
    height: (app.button_scale * 6)+(app.padding*2)
    #height: self.minimum_height
    #height: self.minimum_height if (self.minimum_height >= (app.button_scale * 6)+(app.padding*2)) else int((app.button_scale * 6)+(app.padding * 2))
    GridLayout:
        cols: 2
        spacing: app.padding, 0
        size_hint_y: None
        height: app.button_scale * 6
        GridLayout:
            cols: 1
            size_hint_x: None
            size_hint_y: None
            width: self.minimum_width
            height: app.button_scale * 6
            NormalLabel:
                size_hint_x: None
                width: self.texture_size[0]
                text: 'Preset Name: '
            NormalLabel:
                size_hint_x: None
                width: self.texture_size[0]
                text: 'Folder Name: '
            NormalLabel:
                size_hint_x: None
                width: self.texture_size[0]
                text: 'Naming Method:  '
            NormalLabel:
                size_hint_x: None
                width: self.texture_size[0]
                text: 'Delete Originals: '
            NormalLabel:
                size_hint_x: None
                width: self.texture_size[0]
                text: 'Import To: '
            NormalLabel:
                size_hint_x: None
                width: self.texture_size[0]
                text: 'Database: '

        GridLayout:
            cols: 1
            size_hint_y: None
            height: app.button_scale * 6
            NormalInput:
                size_hint_x: 1
                text: root.title
                multiline: False
                input_filter: app.test_album
                on_focus: root.set_title(self)
            NormalLabel:
                text: root.naming_example
            NormalInput:
                size_hint_x: 1
                text: root.naming_method
                multiline: False
                input_filter: root.test_naming_method
                on_focus: root.new_naming_method(self)
            NormalToggle:
                size_hint_x: 1
                state: 'down' if root.delete_originals == True else 'normal'
                text: str(root.delete_originals)
                on_press: root.set_delete_originals(self.state)
            NormalToggle:
                size_hint_x: 1
                state: 'down' if root.single_folder == True else 'normal'
                text: 'Single Folder' if root.single_folder == True else 'Dated Folders'
                on_press: root.set_single_folder(self.state)
            MenuStarterButtonWide:
                id: importToButton
                size_hint_x: 1
                text: root.import_to
                on_release: root.imports_dropdown.open(self)
    BoxLayout:
        size_hint_y: None
        height: app.button_scale * 6
        orientation: 'vertical'
        NormalLabel:
            text_size: self.size
            halign: 'left'
            valign: 'middle'
            text: 'Import From Folders:'
        Scroller:
            size_hint_y: None
            height: app.button_scale * 4
            NormalTreeView:
                size_hint_y: None
                height: app.button_scale * 4
                id: importPresetFolders
                hide_root: True
                root_options: {'text': 'Import From Folders:', 'font_size':app.text_scale}
        WideButton:
            text: 'Add Folder...'
            on_release: root.add_folder()
""")

class ImportPresetArea(GridLayout):
    """Widget to display and edit all settings for a particular import preset."""

    title = StringProperty()
    import_to = StringProperty('')
    naming_method = StringProperty('')
    last_naming_method = StringProperty('')
    delete_originals = BooleanProperty(False)
    single_folder = BooleanProperty(False)
    preset_index = NumericProperty()
    naming_example = StringProperty('Naming Example')
    owner = ObjectProperty()
    import_from = ListProperty()
    index = NumericProperty()

    def __init__(self, **kwargs):
        super(ImportPresetArea, self).__init__(**kwargs)
        Clock.schedule_once(self.update_import_from)
        app = App.get_running_app()
        self.imports_dropdown = NormalDropDown()
        self.imports_dropdown.basic_animation = True
        database_folders = app.config.get('Database Directories', 'paths')
        database_folders = local_path(database_folders)
        if database_folders.strip(' '):
            databases = database_folders.split(';')
        else:
            databases = []
        for database in databases:
            menu_button = MenuButton(text=database)
            menu_button.bind(on_release=self.change_import_to)
            self.imports_dropdown.add_widget(menu_button)

    def update_preset(self):
        """Updates the app preset setting with the current data."""

        app = App.get_running_app()
        import_preset = {}
        import_preset['title'] = self.title
        import_preset['import_to'] = self.import_to
        import_preset['naming_method'] = self.naming_method
        import_preset['delete_originals'] = self.delete_originals
        import_preset['import_from'] = self.import_from
        import_preset['single_folder'] = self.single_folder
        app.imports[self.index] = import_preset
        self.owner.owner.selected_import = self.index

    def set_title(self, instance):
        if not instance.focus:
            self.title = instance.text
            self.update_preset()
            self.owner.text = instance.text

    def test_naming_method(self, string, *_):
        return "".join(i for i in string if i not in "#%&*{}\\/:?<>+|\"=][;")

    def new_naming_method(self, instance):
        if not instance.focus:
            if not naming(instance.text, title=''):
                self.naming_method = self.last_naming_method
                instance.text = self.last_naming_method
            else:
                self.last_naming_method = instance.text
                self.naming_method = instance.text
                self.naming_example = naming(self.naming_method)
                self.update_preset()

    def set_single_folder(self, state):
        if state == 'down':
            self.single_folder = True
        else:
            self.single_folder = False
        self.update_preset()

    def set_delete_originals(self, state):
        if state == 'down':
            self.delete_originals = True
        else:
            self.delete_originals = False
        self.update_preset()

    def remove_folder(self, index):
        del self.import_from[index]
        self.update_preset()
        self.update_import_from()

    def change_import_to(self, instance):
        self.imports_dropdown.dismiss()
        self.import_to = instance.text
        self.update_preset()

    def add_folder(self):
        content = FileBrowser(ok_text='Add', directory_select=True)
        content.bind(on_cancel=self.owner.owner.dismiss_popup)
        content.bind(on_ok=self.add_folder_confirm)
        self.owner.owner.popup = filepopup = NormalPopup(title='Select A Folder To Import From', content=content, size_hint=(0.9, 0.9))
        filepopup.open()

    def add_folder_confirm(self, *_):
        folder = self.owner.owner.popup.content.filename
        self.import_from.append(folder)
        self.owner.owner.dismiss_popup()
        self.update_preset()
        self.update_import_from()

    def update_import_from(self, *_):
        preset_folders = self.ids['importPresetFolders']
        nodes = list(preset_folders.iterate_all_nodes())
        for node in nodes:
            preset_folders.remove_node(node)
        for index, folder in enumerate(self.import_from):
            preset_folders.add_node(ImportPresetFolder(folder=folder, owner=self, index=index))
        #self.update_preset()