# this file is for comment only.  Not used in production

class Album():


  def album_load_all(self):
    """Scans the album directory, and tries to load all album .ini files into the app.albums variable."""

    self.albums = []
    album_directory = self.album_directory
    if not os.path.exists(album_directory):
      os.makedirs(album_directory)
    album_directory_contents = os.listdir(album_directory)
    for item in album_directory_contents:
      if os.path.splitext(item)[1] == '.ini':
        try:
          configfile = ConfigParser(interpolation=None)
          configfile.read(os.path.join(album_directory, item))
          info = dict(configfile.items('info'))
          album_name = info['name']
          album_description = info['description']
          elements = configfile.items('photos')
          photos = []
          for element in elements:
            photo_path = local_path(element[1])
            if self.Photo.exist(photo_path):
              photos.append(photo_path)
          self.albums.append({'name': album_name, 'description': album_description, 'file': item, 'photos': photos})
        except:
          pass

    def add_album(self, instance=None, answer="yes"):
      """Adds the current input album to the app albums."""

      if answer == 'yes':
        if instance is not None:
          album = instance.ids['input'].text.strip(' ')
          if not album:
            self.dismiss_popup()
            return
        else:
          album_input = self.ids['newAlbum']
          album = album_input.text
          album_input.text = ''
        app = App.get_running_app()
        app.album_make(album, '')
        self.update_treeview()
      self.dismiss_popup()


  def album_make(self, album_name, album_description=''):
    """Create a new album file.
    Arguments:
        album_name: String, name of the album.
        album_description: String, description of album, optional.
    """

    exists = False
    for album in self.albums:
      if album['name'].lower() == album_name.lower():
        exists = True
    if not exists:
      album_filename = album_name + '.ini'
      self.albums.append({'name': album_name, 'description': album_description, 'file': album_filename, 'photos': []})
      self.album_save(self.albums[-1])


  def album_delete(self, index):
    """Deletes an album.
    Argument:
        index: Integer, index of album to delete."""

    filename = os.path.join(self.album_directory, self.albums[index]['file'])
    if os.path.isfile(filename):
      os.remove(filename)
    album_name = self.albums[index]['name']
    del self.albums[index]
    self.message("Deleted the album '" + album_name + "'")


  def album_find(self, album_name):
    """Find an album with a given name.
    Argument:
        album_name: Album name to get.
    Returns: Integer, index of album or -1 if not found.
    """

    for index, album in enumerate(self.albums):
      if album['name'] == album_name:
        return index
    return -1


  def album_update_description(self, index, description):
    """Update the description field for a specific album.
    Arguments:
        index: Integer, index of album to update.
        description: String, new description text.
    """

    self.albums[index]['description'] = description
    self.album_save(self.albums[index])


  def album_save(self, album):
    """Saves an album data file.
    Argument:
        album: Dictionary containing album information:
            file: String, filename of the album (with extension)
            name: String, name of the album.
            description: String, description of the album.
            photos: List of Strings, each is a screenDatabase-relative filepath to a photo in the album.
    """

    configfile = ConfigParser(interpolation=None)
    filename = os.path.join(self.album_directory, album['file'])
    configfile.add_section('info')
    configfile.set('info', 'name', album['name'])
    configfile.set('info', 'description', album['description'])
    configfile.add_section('photos')
    for index, photo in enumerate(album['photos']):
      configfile.set('photos', str(index), agnostic_path(photo))
    with open(filename, 'w') as config:
      configfile.write(config)


  def album_add_photo(self, index, photo):
    """Add a photo to an album.
    Arguments:
        index: Integer, index of the album to update.
        photo: String, screenDatabase-relative path to the new photo.
    """

    self.albums[index]['photos'].append(photo)
    self.album_save(self.albums[index])


  def album_remove_photo(self, index, fullpath, message=False):
    """Find and remove a photo from an album.
    Arguments:
        index: Integer, index of the album to update.
        fullpath: String, screenDatabase-relative path to the photo to remove.
        message: Show an app message stating the photo was removed.
    """

    album = self.albums[index]
    photos = album['photos']
    if fullpath in photos:
      photos.remove(fullpath)
      self.album_save(album)
      if message:
        self.message("Removed photo from the album '" + album['name'] + "'")


  def add_to_album(self, album_name, selected_photos=None):
    """Adds the current selected photos to an album.
    Arguments:
        album_name: String, album to move the photos into.
        selected_photos: List of selected photo data.
    """

    if not selected_photos:
      selected_photos = self.get_selected_photos(fullpath=True)
    app = App.get_running_app()
    added = 0
    for album in app.albums:
      if album['name'] == album_name:
        for photo in selected_photos:
          if photo not in album['photos']:
            album['photos'].append(photo)
            added = added + 1
        app.album_save(album)
    self.select_none()
    if added:
      app.message("Added " + str(added) + " files to the album '" + album_name + "'")
    self.update_treeview()


  def add_to_album_menu(self, instance):
    self.add_to_album(instance.text)
    self.album_menu.dismiss()


  def __append_albums_to_treeview(self, data):
    app = App.get_running_app()
    albums = sorted(app.albums, key=lambda x: x['name'])
    expandable_albums = True if len(albums) > 0 else False
    album_root = {
      'fullpath': 'Albums',
      'folder_name': 'Albums',
      'target': 'Albums',
      'type': 'Album',
      'total_photos': '',
      'displayable': False,
      'expandable': expandable_albums,
      'expanded': True if (self.expanded_albums and expandable_albums) else False,
      'owner': self,
      'indent': 0,
      'subtext': '',
      'height': app.button_scale,
      'end': False,
      'dragable': False
    }
    data.append(album_root)

    self.album_menu.clear_widgets()
    for album in albums:
      total_photos = len(album['photos'])
      menu_button = MenuButton(text=album['name'])
      menu_button.bind(on_release=self.add_to_album_menu)
      self.album_menu.add_widget(menu_button)
      if self.expanded_albums:
        if total_photos > 0:
          total_photos_text = '(' + str(total_photos) + ')'
        else:
          total_photos_text = ''
        album_item = {
          'fullpath': album['name'],
          'folder_name': album['name'],
          'total_photos': total_photos_text,
          'total_photos_numeric': total_photos,
          'target': album['name'],
          'type': 'Album',
          'displayable': True,
          'expandable': False,
          'owner': self,
          'indent': 1,
          'subtext': '',
          'height': app.button_scale,
          'end': False,
          'dragable': False
        }
        data.append(album_item)
    data[-1]['end'] = True
    data[-1]['height'] = data[-1]['height'] + int(app.button_scale * 0.1)
