from kivy.compat import text_type

from screenSettings.SettingString import SettingString


class SettingNumeric(SettingString):
    def _validate(self, instance, answer):
        # we know the type just by checking if there is a '.' in the original value
        is_float = '.' in str(self.value)
        value = self.popup.content.ids['input'].text
        self.dismiss()
        if answer == 'yes':
            try:
                if is_float:
                    self.value = text_type(float(value))
                else:
                    self.value = text_type(int(value))
            except ValueError:
                return