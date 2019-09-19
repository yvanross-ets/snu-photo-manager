import os

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout

from generalElements.ExpandableButton import ExpandableButton
from screenAlbum import ExternalProgramEditor

from kivy.lang.builder import Builder

Builder.load_string("""
<EditMain>:
    padding: 0, 0, int(app.button_scale / 2), 0
    cols: 1
    size_hint: 1, None
    height: self.minimum_height
    WideButton:
        text: 'Basic Color Adjustments'
        on_release: root.owner.set_edit_panel('color')
        disabled: not root.owner.view_image and not root.owner.ffmpeg
    SmallBufferY:
    WideButton:
        text: 'Advanced Color Adjustments'
        on_release: root.owner.set_edit_panel('advanced')
        disabled: not root.owner.view_image and not root.owner.ffmpeg
    SmallBufferY:
    WideButton:
        text: 'Filters'
        on_release: root.owner.set_edit_panel('filter')
        disabled: not root.owner.view_image and not root.owner.ffmpeg
    SmallBufferY:
    WideButton:
        text: 'Image Borders'
        on_release: root.owner.set_edit_panel('border')
        disabled: not root.owner.view_image and not root.owner.ffmpeg
    SmallBufferY:
    WideButton:
        height: app.button_scale if root.owner.opencv else 0
        opacity: 1 if root.owner.opencv else 0
        text: 'Denoise'
        on_release: root.owner.set_edit_panel('denoise')
        disabled: (not root.owner.view_image and not root.owner.ffmpeg) or not root.owner.opencv
    SmallBufferY:
        height: int(app.button_scale / 4) if root.owner.opencv else 0
    WideButton:
        text: 'Rotate'
        on_release: root.owner.set_edit_panel('rotate')
        disabled: (not root.owner.view_image and not root.owner.ffmpeg) or not root.owner.opencv
    SmallBufferY:
    WideButton:
        text: 'Crop'
        on_release: root.owner.set_edit_panel('crop')
        disabled: (not root.owner.view_image and not root.owner.ffmpeg) or not root.owner.opencv
    SmallBufferY:
    WideButton:
        text: 'Convert'
        on_release: root.owner.set_edit_panel('convert')
        disabled: root.owner.view_image or not root.owner.ffmpeg
    LargeBufferY:
    WideButton:
        id: deleteOriginal
        text: 'Delete Unedited Original File'
        warn: True
        on_release: root.owner.delete_original()
    SmallBufferY:
    WideButton:
        id: deleteOriginalAll
        text: 'Delete All Originals In Folder'
        warn: True
        on_release: root.owner.delete_original_all()
    SmallBufferY:
    WideButton:
        id: undoEdits
        text: 'Restore Original Unedited File'
        on_release: root.owner.restore_original()
    LargeBufferY:
    GridLayout:
        cols: 2
        size_hint_y: None
        height: app.button_scale
        LeftNormalLabel:
            size_hint_x: 1
            text: 'External Programs:'
        NormalButton:
            size_hint_x: None
            text: 'New'
            on_release: root.owner.add_program()
    GridLayout:
        id: externalPrograms
        height: self.minimum_height
        size_hint_y: None
        cols: 1

""")

class EditMain(GridLayout):
    """Main menu edit panel, contains buttons to activate the other edit panels."""

    owner = ObjectProperty()

    def __init__(self, **kwargs):
        super(EditMain, self).__init__(**kwargs)
        self.update_programs()
        self.refresh_buttons()

    def refresh_buttons(self):
        self.update_undo()
        self.update_delete_original()
        self.update_delete_original_all()

    def save_last(self):
        pass

    def load_last(self):
        pass

    def update_delete_original(self):
        """Checks if the current viewed photo has an original file, enables the 'Delete Original' button if so."""

        delete_original_button = self.ids['deleteOriginal']
        if os.path.isfile(self.owner.photoinfo[10]):
            delete_original_button.disabled = False
        else:
            delete_original_button.disabled = True

    def update_delete_original_all(self):
        """Checks if currently viewing a folder, enables 'Delete All Originals' button if so."""

        delete_original_all_button = self.ids['deleteOriginalAll']
        if self.owner.type == 'Folder':
            delete_original_all_button.disabled = False
        else:
            delete_original_all_button.disabled = True

    def update_undo(self):
        """Checks if the current viewed photo has an original file, enables the 'Restore Original' button if so."""

        undo_button = self.ids['undoEdits']
        if os.path.isfile(self.owner.photoinfo[10]):
            undo_button.disabled = False
        else:
            undo_button.disabled = True

    def save_program(self, index, name, command, argument):
        """Saves an external program command to the app settings.
        Arguments:
            index: Index of the program to edit in the external program list.
            name: Name of the program
            command: Path to the executable file of the program
            argument: Extra arguments for the program command
        """

        app = App.get_running_app()
        app.program_save(index, name, command, argument)
        #self.update_programs(expand=True, expand_index=index)

    def remove_program(self, index):
        """Removes a program from the external programs list.
        Argument:
            index: Index of the program to remove in the external program list.
        """

        app = App.get_running_app()
        app.program_remove(index)
        self.update_programs()

    def update_programs(self, expand=False, expand_index=-1):
        """Updates the external programs list in this panel.
        Arguments:
            expand: Boolean, set to True to set an external program to edit mode.
            expand_index: Integer, index of the external program to be in edit mode.
        """

        external_programs = self.ids['externalPrograms']
        app = App.get_running_app()
        external_programs.clear_widgets()

        if expand_index == -1:
            expand_index = len(app.programs)-1
        for index, preset in enumerate(app.programs):
            name, command, argument = preset
            program_button = ExpandableButton(text=name, index=index)
            program_button.bind(on_release=lambda button: app.program_run(button.index, button))
            program_button.bind(on_remove=lambda button: self.remove_program(button.index))
            program_button.content = ExternalProgramEditor(index=index, name=name, command=command, argument=argument, owner=self)
            external_programs.add_widget(program_button)
            if index == expand_index and expand:
                program_button.expanded = True