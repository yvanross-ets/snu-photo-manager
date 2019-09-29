from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.gridlayout import GridLayout

from filebrowser import FileBrowser
from generalElements.popups.NormalPopup import NormalPopup
from kivy.lang.builder import Builder

Builder.load_string("""
<ExternalProgramEditor>:
    cols: 1
    height: app.button_scale * 6
    size_hint: 1, None
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        ShortLabel:
            text: 'Name: '
        NormalInput:
            text: root.name
            multiline: False
            input_filter: app.remove_unallowed_characters
            on_focus: root.set_name(self)
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        ShortLabel:
            text: 'Command: '
        WideButton:
            text: root.command
            text_size: (self.size[0] - app.padding*2, None)
            shorten: True
            on_release: root.select_command()
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        ShortLabel:
            text: 'Argument: '
        NormalInput:
            text: root.argument
            multiline: False
            input_filter: app.remove_unallowed_characters
            on_focus: root.set_argument(self)
    LeftNormalLabel:
        text: 'For The Argument: '
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        ShortLabel:
            text: '"%i"'
        LeftNormalLabel:
            text: 'Is the image filename'
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: app.button_scale
        ShortLabel:
            text: '"%%"'
        LeftNormalLabel:
            text: 'Is a single "%"'
""")

class ExternalProgramEditor(GridLayout):
    """Widget to display and edit an external program command."""

    name = StringProperty()  #Command name
    command = StringProperty()  #Command to run
    argument = StringProperty()  #Command argument, added to the end of 'command'
    owner = ObjectProperty()
    index = NumericProperty()

    def save_program(self):
        self.owner.save_program(self.index, self.name, self.command, self.argument)

    def set_name(self, instance):
        if not instance.focus:
            self.name = instance.text
            self.save_program()
            self.parent.parent.text = instance.text

    def set_argument(self, instance):
        if not instance.focus:
            self.argument = instance.text
            self.save_program()

    def select_command(self):
        """Opens a popup filebrowser to select a program to run."""

        content = FileBrowser(ok_text='Select', filters=['*'])
        content.bind(on_cancel=lambda x: self.owner.owner.dismiss_popup())
        content.bind(on_ok=self.select_command_confirm)
        self.owner.owner.popup = filepopup = NormalPopup(title='Select A Program', content=content, size_hint=(0.9, 0.9))
        filepopup.open()

    def select_command_confirm(self, *_):
        """Called when the filebrowser dialog is successfully closed."""

        self.command = self.owner.owner.popup.content.filename
        self.owner.owner.dismiss_popup()
        self.save_program()