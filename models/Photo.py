#https://docs.sqlalchemy.org/en/13/orm/tutorial.html
import os
from models.Database import Database
from generalcommands import agnostic_path,local_path,agnostic_photoinfo, local_paths,local_thumbnail, isfile2
from generalconstants import imagetypes,movietypes
import sqlite3
from main.SQLMultiThreadOK import SQLMultiThreadOK

from PIL import Image, ImageEnhance
from io import BytesIO
from ffpyplayer.pic import SWScale
from ffpyplayer.player import MediaPlayer
import sqlite3

class Photo(Database):
  ID=0
  FULLPATH=1
  FOLDER=2
  DATABASEFOLDER=3
  ORIGINALDATE=4
  ORIGINALSIZE=5
  RENAME=6
  IMPORTDATE=7
  MODIFYDATE=8
  EDITED=9
  ORIENTATION=10
  THUMBNAIL=11


  def __init__(self,app,database):
    super(Photo,self).__init__(app=app,database=database)
    self.__create()


  def insert(self, folderId, full_filename, fileinfo):
    """Add a new photo to the screenDatabase.
    Argument:
        fileinfo: List, a photoinfo object.
    """
    thumbnail = self.__generate_thumbnail(local_path(full_filename))
    thumbnail = sqlite3.Binary(thumbnail)

    self.database.execute("insert into photos(FullPath, FolderId, DatabaseFolder, OriginalDate, OriginalSize, Rename, ImportDate, ModifiedDate,  Edited, Orientation, Thumbnail) values(?,?,?,?,?,?,?,?,?,?,?)",(
    fileinfo.fullpath, folderId, fileinfo.database_folder, fileinfo.original_date, fileinfo.original_size[0],
    fileinfo.rename, fileinfo.import_date, fileinfo.modified_date, fileinfo.edited, fileinfo.orientation, thumbnail))
    self.commit()

  def update(self, fileinfo):
    """Updates a photo's screenDatabase entry with new info.
    Argument:
        fileinfo: List, a photoinfo object.
    """

    fileinfo = agnostic_photoinfo(fileinfo)
    self.database.execute(
      "UPDATE photos SET Rename = ?, ModifiedDate = ?,  Edited = ?, Orientation = ?, Persons = ? WHERE FullPath = ?",
      (
        fileinfo[Photo.RENAME],
        fileinfo[Photo.MODIFYDATE],
        fileinfo[Photo.EDITED],
        fileinfo[Photo.ORIENTATION],
        fileinfo[Photo.FULLPATH]))
    self.commit()

  def move(self, fileinfo):
        """Updates a photo's screenDatabase folder.
        Argument:
            fileinfo: list, a photoinfo object.
        """

        fileinfo = agnostic_photoinfo(fileinfo)
        self.database.execute("UPDATE photos SET DatabaseFolder = ? WHERE FullPath = ?", (fileinfo[Photo.DATABASEFOLDER], fileinfo[Photo.FULLPATH]))


  def thumbnail(self,fullpath,temporary=False):
    fullpath = agnostic_path(fullpath)
    thumbnail = self.database.execute('SELECT * FROM photos WHERE FullPath = ?', (fullpath,))

    thumbnail = list(thumbnail)
    if thumbnail:
      thumbnail = local_thumbnail(list(thumbnail[Photo.THUMBNAIL]))
    return thumbnail

  def thumbnail_write(self, fullpath, modified_date, thumbnail, orientation, temporary=False):
        """Save or updates a thumbnail to the thumbnail screenDatabase.
        Arguments:
            fullpath: String, screenDatabase-relative path to the photo.
            modified_date: Integer, the modified date of the original photo file.
            thumbnail: Thumbnail image data.
            orientation: Integer, EXIF orientation code.
            temporary: Boolean, if True, save to the temporary thumbnails screenDatabase.
        """
        fullpath = agnostic_path(fullpath)
        self.database.execute("UPDATE photos SET ModifiedDate = ?, Thumbnail = ?, Orientation = ? WHERE FullPath = ?", (modified_date, thumbnail, orientation, fullpath, ))

  def thumbnail_update(self, fullpath, database, modified_date, orientation, temporary=False, force=False):
    """Check if a thumbnail is already in screenDatabase, check if out of date, update if needed.
    Arguments:
        fullpath: String, the screenDatabase-relative path to the photo.
        database: String, screenDatabase directory the photo is in.
        modified_date: Integer, the modified date of the original photo.
        orientation: Integer, EXIF orientation code.
        temporary: Boolean, if True, uses the temporary thumbnails screenDatabase.
        force: Boolean, if True, will always update thumbnail, regardless of modified date.
    Returns: Boolean, True if thumbnail updated, False if not.
    """

    # check if thumbnail is already in screenDatabase, check if out of date, update if needed
    matches = self.thumbnail(fullpath, temporary=temporary)
    if matches:
      if modified_date <= matches[1] and not force:
        return False
    thumbnail = self.__generate_thumbnail(local_path(fullpath), local_path(database))
    thumbnail = sqlite3.Binary(thumbnail)
    self.Photo.thumbnail_write(fullpath=fullpath, modified_date=modified_date, thumbnail=thumbnail,
                               orientation=orientation, temporary=temporary)
    return True

  #database_get_folder
  def by_folder_id(self, folder_id):
    """Get photos in a folder.
    Argument:
        folder: String, screenDatabase-relative folder name to get.
    Returns: List of photoinfo Lists.
    """

    # if database:
    #   database = agnostic_path(database)
    #   photos = list(
    #     self.database.execute('SELECT * FROM photos WHERE Folder = ? AND DatabaseFolder = ?', (folder, database,)))
    # else:
    cmd = "select * from photos where FolderId = %d" % int(folder_id)
    photos = list(self.database.execute(cmd))
    return local_paths(photos)


  def find_by_fullpath(self,fullpath):
    fullpath = agnostic_path(fullpath)
    photo = self.database.execute('SELECT * FROM photos WHERE FullPath = ?', (fullpath,))
    photo = list(photo)
    if photo:
      photo = list(photo[0])
      photo[0] = local_path(photo[0])
    return photo

  def exist(self,fullpath):
    if not isinstance(fullpath,str):
      raise ValueError('filepath must be of type string',fullpath)

    filename_matches = list(self.database.execute('SELECT * FROM photos WHERE fullpath = ?', (fullpath,)))
    if filename_matches:
      return filename_matches[0]
    return False

  def delete_folder(self,folder):
    self.database.execute('DELETE FROM photos WHERE folder = ?', (agnostic_path(folder),))
    self.commit()

  # def get_folder_treeview_info(self):
  #     folders = []
  #     folder_items = list(self.database.execute('SELECT * FROM photos'))
  #     for item in folder_items:
  #       folders.append([local_path(item[Photo.FOLDER]),'',''])  #title, description
  #     return folders

  def folders(self):
    folders_out = []
    folder_items = list(self.database.execute('SELECT distinct(fullpath) FROM photos'))
    for item in folder_items:
      folders_out.append(local_path(item[0]))
    return folders_out

  def folder_exist(self,folder):
    folder = agnostic_path(folder)
    matches = self.database.execute('SELECT * FROM photos WHERE folder = ?', (folder,))
    matches = list(matches)
    if matches:
      matches = list(matches[0])
      matches[0] = local_path(matches[0])
    return matches

  def delete_by_fullpath(self,fullpath):
    fullpath = agnostic_path(fullpath)
    self.database.execute('DELETE FROM photos WHERE FullPath = ?', (fullpath,))


  def delete_file(self, fullpath, filename, message=False):
    """Deletes a photo file, and removes it from the screenDatabase.
    Arguments:
        fullpath: String, screenDatabase identifier for the photo to delete.
        filename: Full path to the photo to delete.
        message: Display an app message that the file was deleted.
    """

    photoinfo = self.exist(fullpath)
    if os.path.isfile(filename):
      deleted = self.app.delete_file(filename)
    else:
      deleted = True
    if deleted is True:
      if os.path.isfile(photoinfo[10]):
        self.app.delete_file(photoinfo[10])

      self.Photo.delete_by_fullpath(fullpath)
      if message:
        self.app.message("Deleted the file '" + filename + "'")
      return True
    else:
      if message:
        self.app.popup_message(text='Could not delete file', title='Warning')
      return deleted

  def rename(self, fullpath, newname, newfolder, dontcommit=False):
        """Changes the screenDatabase-relative path of a photo to another path.
        Updates both photos and thumbnails databases.
        Arguments:
            fullpath: String, the original screenDatabase-relative path.
            newname: String, the new screenDatabase-relative path.
            newfolder: String, new screenDatabase-relative containing folder for the file.
            dontcommit: Dont write to the screenDatabase when finished.
        """

        fullpath = agnostic_path(fullpath)
        newname = agnostic_path(newname)
        if self.exist(newname):
            self.delete_by_fullpath(newname)

        newfolder_rename = agnostic_path(newfolder)
        self.database.execute("UPDATE photos SET FullPath = ?, Folder = ? WHERE FullPath = ?", (newname, newfolder_rename, fullpath, ))
        if not dontcommit:
            self.commit()


  def clean(self,deep=False):
    databases = self.app.get_database_directories()

    # remove referenced files if the screenDatabase that contained them is no longer loaded
    found_databases = list(self.database.execute('SELECT DatabaseFolder FROM photos GROUP BY DatabaseFolder'))
    for database in found_databases:
      if local_path(database[0]) not in databases:
        self.database.execute('DELETE FROM photos WHERE DatabaseFolder = ?', (database[0],))

    # remove references if the photos are not found
    for database in databases:
      if os.path.isdir(database) or deep:
        database_renamed = agnostic_path(database)
        photos = list(self.database.execute('SELECT * FROM photos WHERE DatabaseFolder = ?', (database_renamed,)))
        for photo in photos:
          photo_file = os.path.join(local_path(photo[2]), local_path(photo[0]))
          if not isfile2(photo_file):
            self.Photo.delete_by_fullpath(photo[Photo.FULLPATH])

  def __generate_thumbnail(self, full_filename):
    """Creates a thumbnail image for a photo.

    Arguments:
        fullpath: Path to file, relative to the screenDatabase folder.
        database_folder: Database root folder where the file is.
    Returns:
        A thumbnail jpeg
    """

    thumbnail = ''
    #full_filename = os.path.join(database_folder, fullpath)
    extension = os.path.splitext(full_filename)[1].lower()

    try:
      if extension in imagetypes:
        # This is an image file, use PIL to generate a thumnail
        image = Image.open(full_filename)
        image.thumbnail((self.app.thumbsize, self.app.thumbsize), Image.ANTIALIAS)
        if image.mode != 'RGB':
          image = image.convert('RGB')
        output = BytesIO()
        image.save(output, 'jpeg')
        thumbnail = output.getvalue()

      elif extension in movietypes:
        # This is a video file, use ffpyplayer to generate a thumbnail
        player = MediaPlayer(full_filename, ff_opts={'paused': True, 'ss': 1.0, 'an': True})
        frame = None
        while not frame:
          frame, value = player.get_frame(force_refresh=True)
        player.close_player()
        player = None
        frame = frame[0]
        frame_size = frame.get_size()
        frame_converter = SWScale(frame_size[0], frame_size[1], frame.get_pixel_format(), ofmt='rgb24')
        new_frame = frame_converter.scale(frame)
        image_data = bytes(new_frame.to_bytearray()[0])

        image = Image.frombuffer(mode='RGB', size=(frame_size[0], frame_size[1]), data=image_data, decoder_name='raw')
        image = image.transpose(1)

        image.thumbnail((self.app.thumbsize, self.app.thumbsize), Image.ANTIALIAS)
        output = BytesIO()
        image.save(output, 'jpeg')
        thumbnail = output.getvalue()
      return thumbnail
    except Exception as e:
      print(e)
      return None



  def __create(self):

    try:
      matches = self.database.execute('SELECT * FROM photos ')
    except:
      self.database.execute('''CREATE TABLE IF NOT EXISTS photos(
                                 Id integer primary key autoincrement,
                                 FullPath text not null,
                                 FolderId integer not null,
                                 DatabaseFolder text not null,
                                 OriginalDate integer not null,
                                 OriginalSize integer not null,
                                 Rename text,
                                 ImportDate integer not null,
                                 ModifiedDate integer not null,
                                 Edited integer,
                                 Orientation integer,
                                 Thumbnail blob);''')

      self.database.execute('''
        CREATE INDEX "photo_FullPath" ON "photos" ("FullPath");
       ''')

      self.database.execute('''
        CREATE INDEX "photo_DatabaseFolder" ON "photos" ("DatabaseFolder");
       ''')

      self.database.execute('''
        CREATE INDEX "photo_FolderId" ON "photos" ("FolderId");
       ''')



# if not restore:
#     self.tempthumbnails = SQLMultiThreadOK(':memory:')
#     self.tempthumbnails.execute('''CREATE TABLE IF NOT EXISTS thumbnails(
#                                 FullPath text PRIMARY KEY,
#                                 ModifiedDate integer,
#                                 Thumbnail blob,
#                                 Orientation integer);''')
#