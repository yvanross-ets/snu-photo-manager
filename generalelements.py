from kivy.config import Config

Config.window_icon = "data/icon.png"

from kivy.lang.builder import Builder
Builder.load_string("""
<SmallBufferY@Widget>:
    size_hint_y: None
    height: int(app.button_scale / 4)

<MediumBufferY@Widget>:
    size_hint_y: None
    height: int(app.button_scale / 2)

<LargeBufferY@Widget>:
    size_hint_y: None
    height: app.button_scale

<SmallBufferX@Widget>:
    size_hint_x: None
    width: int(app.button_scale / 4)

<MainHeader@HeaderBase>:
    canvas.before:
        Color:
            rgba: app.theme.header_main_background
        Rectangle:
            size: self.size
            pos: self.pos
            source: 'data/headerbglight.png'
    height: int(app.button_scale * 1.25)
    padding: int(app.button_scale / 8)
    
<MediumBufferX@Widget>:
    size_hint_x: None
    width: int(app.button_scale / 2)

<LargeBufferX@Widget>:
    size_hint_x: None
    width: app.button_scale

<HeaderBase@BoxLayout>:
    size_hint_y: None
    orientation: 'horizontal'

<Header@HeaderBase>:
    canvas.before:
        Color:
            rgba: app.theme.header_background
        Rectangle:
            size: self.size
            pos: self.pos
            source: 'data/headerbg.png'
    height: app.button_scale


<MainArea@BoxLayout>:
    canvas.before:
        Color:
            rgba: app.theme.main_background
        Rectangle:
            size: self.size
            pos: self.pos
            source: 'data/mainbg.png'

<-NormalSlider@Slider>:
    #:set sizing 18
    canvas:
        Color:
            rgba: app.theme.slider_background
        BorderImage:
            border: (0, sizing, 0, sizing)
            pos: self.pos
            size: self.size
            source: 'data/sliderbg.png'
        Color:
            rgba: app.theme.slider_grabber
        Rectangle:
            pos: (self.value_pos[0] - app.button_scale/4, self.center_y - app.button_scale/2)
            size: app.button_scale/2, app.button_scale
            source: 'data/buttonflat.png'
    size_hint_y: None
    height: app.button_scale
    min: -1
    max: 1
    value: 0

<-HalfSlider@Slider>:
    #:set sizing 18
    canvas:
        Color:
            rgba: app.theme.slider_background
        BorderImage:
            border: (0, sizing, 0, sizing)
            pos: self.pos
            size: self.size
            source: 'data/sliderbg.png'
        Color:
            rgba: app.theme.slider_grabber
        Rectangle:
            pos: (self.value_pos[0] - app.button_scale/4, self.center_y - app.button_scale/2)
            size: app.button_scale/2, app.button_scale
            source: 'data/buttonflat.png'
    size_hint_y: None
    height: app.button_scale
    min: 0
    max: 1
    value: 0

<LeftNormalLabel@NormalLabel>:
    mipmap: True
    shorten: True
    shorten_from: 'right'
    font_size: app.text_scale
    size_hint_x: 1
    text_size: self.size
    halign: 'left'
    valign: 'middle'



<DatabaseLabel@ShortLabel>:
    mipmap: True
    text: app.database_update_text

<HeaderLabel@Label>:
    mipmap: True
    color: app.theme.header_text
    font_size: int(app.text_scale * 1.5)
    size_hint_y: None
    height: app.button_scale
    bold: True


<BubbleContent>:
    canvas:
        Clear:
    opacity: .7 if self.disabled else 1
    rows: 1

<MenuStarterButton@ButtonBase>:
    canvas.after:
        Color:
            rgba: self.color
        Rectangle:
            pos: (root.pos[0]+root.width-(root.height/1.5)), root.pos[1]
            size: root.height/2, root.height
            source: 'data/menuarrows.png'
    menu: True
    size_hint_y: None
    height: app.button_scale
    shorten: True
    shorten_from: 'right'
    font_size: app.text_scale
    size_hint_max_x: self.texture_size[0] + (app.button_scale * 1.2)

<MenuStarterButtonWide@ButtonBase>:
    canvas.after:
        Color:
            rgba: self.color
        Rectangle:
            pos: (root.pos[0]+root.width-(root.height/1.5)), root.pos[1]
            size: root.height/2, root.height
            source: 'data/menuarrows.png'
    menu: True
    size_hint_y: None
    height: app.button_scale
    text_size: self.size
    halign: 'center'
    valign: 'middle'
    shorten: True
    shorten_from: 'right'
    font_size: app.text_scale
    size_hint_x: 1

<NormalToggle@ToggleBase>:
    toggle: True
    size_hint_x: None
    width: self.texture_size[0] + 20

<ReverseToggle@ToggleBase>:
    canvas:
        Color:
            rgba: self.color
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'data/arrowdown.png' if self.state == 'normal' else 'data/arrowup.png'
    menu: True
    size_hint: None, None
    height: app.button_scale
    width: app.button_scale

<SettingsButton@NormalButton>:
    text: '' if app.simple_interface else 'Settings'
    border: (0, 0, 0, 0) if app.simple_interface else (16, 16, 16, 16)
    background_normal: 'data/settings.png' if app.simple_interface else 'data/button.png'
    background_down: 'data/settings.png' if app.simple_interface else 'data/button.png'
    on_release: app.open_settings()


<SimpleRecycleItem@RecycleItem>:
    NormalLabel:
        size_hint_y: None
        height: app.button_scale
        text_size: (self.width - 20, None)
        text: root.text
        halign: 'left'
        valign: 'center'

<SelectableRecycleGridWide@SelectableRecycleGrid>:
    cols: max(1, int(self.width / ((app.button_scale * 8) + (app.button_scale / 2))))
    default_size: (app.button_scale * 8), (app.button_scale * 4)

<NormalTreeView@TreeView>:
    color_selected: app.theme.selected
    odd_color: app.list_background_odd
    even_color: app.list_background_even
    indent_level: int(app.button_scale * .5)
    size_hint: 1, None
    height: self.minimum_height
    hide_root: True


<ColorPickerCustom_Label@Label>:
    mroot: None
    size_hint_x: None
    width: '30sp'
    text_size: self.size
    halign: "center"
    valign: "middle"

<ColorPickerCustom_Selector@BoxLayout>:
    foreground_color: None
    text: ''
    mroot: None
    mode: 'rgb'
    color: 0
    spacing: '2sp'
    ColorPickerCustom_Label:
        text: root.text
        mroot: root.mroot
        color: root.foreground_color or (1, 1, 1, 1)
    Slider:
        id: sldr
        size_hint: 1, .25
        pos_hint: {'center_y':.5}
        range: 0, 255
        value: root.color * 255
        on_value:
            root.mroot._trigger_update_clr(root.mode, root.clr_idx, args[1])


""")


