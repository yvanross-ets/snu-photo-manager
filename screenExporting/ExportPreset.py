from kivy.app import App
from kivy.clock import Clock
from kivy.properties import DictProperty, ObjectProperty

from generalElements.ExpandableButton import ExpandableButton
from screenExporting.ExportPresetArea import ExportPresetArea


class ExportPreset(ExpandableButton):
    data = DictProperty()
    owner = ObjectProperty()

    def on_data(self, *_):
        export_preset = self.data
        self.content = ExportPresetArea(owner=self, index=self.index, name=export_preset['name'], export=export_preset['export'], ftp_address=export_preset['ftp_address'], ftp_user=export_preset['ftp_user'], ftp_password=export_preset['ftp_password'], ftp_passive=export_preset['ftp_passive'], ftp_port=export_preset['ftp_port'], export_folder=export_preset['export_folder'], create_subfolder=export_preset['create_subfolder'], export_info=export_preset['export_info'], scale_image=export_preset['scale_image'], scale_size=export_preset['scale_size'], scale_size_to=export_preset['scale_size_to'], jpeg_quality=export_preset['jpeg_quality'], watermark=export_preset['watermark'], watermark_image=export_preset['watermark_image'], watermark_opacity=export_preset['watermark_opacity'], watermark_horizontal=export_preset['watermark_horizontal'], watermark_vertical=export_preset['watermark_vertical'], watermark_size=export_preset['watermark_size'], ignore_tags=' '.join(export_preset['ignore_tags']), export_videos=export_preset['export_videos'])

    def on_expanded(self, *_):
        if self.content:
            content_container = self.ids['contentContainer']
            if self.expanded:
                Clock.schedule_once(self.content.update_test_image)
        super(ExportPreset, self).on_expanded()

    def on_remove(self):
        app = App.get_running_app()
        app.export_preset_remove(self.index)
        self.owner.selected_preset = -1
        self.owner.update_treeview()

    def on_release(self):
        self.owner.selected_preset = self.index
        self.owner.export()