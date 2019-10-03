import os
import sqlite3
import time
from io import BytesIO
from datetime import datetime
from generalconstants import imagetypes, movietypes
from PIL import Image
from sqlalchemy import Column, String, Integer, Boolean, Float, BLOB
from sqlalchemy import Sequence
from sqlalchemy import Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from ffpyplayer.player import MediaPlayer
from ffpyplayer.pic import SWScale
from generalcommands import naming
from kivy.app import App
from models.BaseModel import BaseModel
try:
    from configparser import ConfigParser
except:
    from six.moves import configparser

Base = declarative_base()

photos_tags = Table('photos_tags', Base.metadata,
                    Column('photo_id', Integer, ForeignKey('photo.id')),
                    Column('tag_id', Integer, ForeignKey('tag.id'))
                    )


# class PhotosTags(Base):
#     __tablename__ = 'photos_tags'
#
#     photo_id = Column(Integer,  ForeignKey('photos.id'), primary_key =True)
#     tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)
#
#     def __repr__(self):
#         return "<PhotoTag(photo_id='%s', tag_id='%s')>" % (
#             self.photo_id, self.tag_id)
#
#     def create_table(engine):
#         PhotosTags.__table__
#         Base.metadata.create_all(engine)

class Photo(Base, BaseModel):
    __tablename__ = 'photo'

    id = Column(Integer, Sequence('photo_id_seq'), primary_key=True)
    full_path = Column(String)
    database_folder = Column(String)
    original_date = Column(Integer)
    original_size = Column(Integer)
    original_file = Column(String)
    rename = Column(String)
    import_date = Column(Integer)
    modify_date = Column(Integer)
    owner = Column(String)
    edited = Column(Boolean)
    export = Column(Boolean)
    orientation = Column(Integer)
    latitude = Column(Float, default=0)
    longitude = Column(Float, default=0)
    thumbnail = Column(BLOB)
    folder_id = Column(Integer, ForeignKey('folder.id'))
    imported_tags = ""
    tags = relationship('Tag', secondary=photos_tags, back_populates='photos')
    folder = relationship('Folder', back_populates='photos')
    name = 'Photo 1234'
    fullpath = "12345678"

    def __repr__(self):
        if (self.longitude):
            return "<Photo( id='%s',fullpath='%s', folder='%s', database_folder='%s', original_file='%s',original_date='%s', original_size='%s', rename='%s', import_date='%s', modify_date='%s',edited='%s', orientation='%s', latitude='%s', longitude='%s', owner='%s')>" % (
                self.id, self.full_path, self.folder, self.database_folder, self.original_file, self.original_date,
                self.original_size,
                self.rename, self.import_date, self.modify_date, self.edited, self.orientation, self.latitude,
                self.longitude, self.owner)
        else:
            return "<Photo( id='%s',fullpath='%s', folder='%s', database_folder='%s', original_file='%s',original_date='%s', original_size='%s', rename='%s', import_date='%s', modify_date='%s',edited='%s', orientation='%s', owner='%s')>" % (
                self.id, self.full_path, self.folder, self.database_folder, self.original_file, self.original_date,
                self.original_size,
                self.rename, self.import_date, self.modify_date, self.edited, self.orientation, self.owner)

    def create_table(engine):
        Photo.__table__
        Base.metadata.create_all(engine)

    def from_file_info(self, file_info):

        filepath, filename = os.path.split(file_info[0])
        database_folder = file_info[1]
        full_folder = os.path.join(database_folder, filepath)
        full_filename = os.path.join(full_folder, filename)
        full_folder = os.path.join(database_folder, filepath)
        original_file = filename
        original_date = int(os.path.getmtime(full_filename))
        modify_date = original_date
        original_size = int(os.path.getsize(full_filename))
        import_date = int(time.time() - time.timezone)
        longitude = latitude = None
        orientation = 0

        if not self.modify_date:
            modify_date = int(os.path.getmtime(full_filename))

        edited = 0
        owner = ''
        export = 1
        rename = filename

        # Try to read various information from info files that may exist.
        infofile = os.path.join(full_folder, '.picasaoriginals')
        if os.path.isdir(infofile):
            originals = os.listdir(infofile)
            if filename in originals:
                original_file = os.path.join('.picasaoriginals', filename)
                full_original_file = os.path.join(full_folder, original_file)
                original_date = int(os.path.getmtime(full_original_file))
                original_size = int(os.path.getsize(full_original_file))
                edited = 1

        infofile = os.path.join(full_folder, '.originals')
        if os.path.isdir(infofile):
            originals = os.listdir(infofile)
            if filename in originals:
                original_file = os.path.join('.originals', filename)
                full_original_file = os.path.join(full_folder, original_file)
                original_date = int(os.path.getmtime(full_original_file))
                original_size = int(os.path.getsize(full_original_file))
                edited = 1

        infofile = os.path.join(full_folder, '.picasa.ini')
        if os.path.isfile(infofile):
            configfile = ConfigParser(interpolation=None)
            try:
                configfile.read(infofile)
                configitems = configfile.items(filename)
                if ('star', 'yes') in configitems:
                    self.imported_tags += 'favorite,'
            except:
                pass

        infofile = os.path.join(full_folder, '.photoinfo.ini')
        if os.path.isfile(infofile):
            configfile = ConfigParser(interpolation=None)
            try:
                configfile.read(infofile)
                configitems = dict(configfile.items(filename))
                if 'tags' in configitems:
                    self.imported_tags += configitems['tags']
                if 'owner' in configitems:
                    owner = configitems['owner']
                if 'edited' in configitems:
                    edited = int(configitems['edited'])
                if 'import_date' in configitems:
                    import_date = int(configitems['import_date'])
                if 'rename' in configitems:
                    rename = configitems['rename']
                if 'export' in configitems:
                    export = int(configitems['export'])
            except:
                pass

        # try to read the photo orientation from the exif tag
        # http: // geospatialtraining.com / extracting - geographic - coordinates -
        # = Degrees + Minutes / 60 + Seconds / 3600
        orientation = 1
        try:

            image = Image.open(full_filename)

            exif_tag = image._getexif()
            if 274 in exif_tag:
                orientation = exif_tag[274]
            if 36867 in exif_tag:
                original_exif_date = exif_tag[36867]
                extracted_date = datetime.strptime(original_exif_date, '%Y:%m:%d  %H:%M:%S')
                original_date = extracted_date.timestamp()
            if 34853 in exif_tag:
                latitude, longitude = self.get_lat_lon4(exif_tag[34853][1], exif_tag[34853][2], exif_tag[34853][3],
                                                        exif_tag[34853][4])

        except Exception as e:
            print("ERROR:", e)
            pass

        # always set original_date and original_file before calling new_folder_name
        self.original_date = original_date
        self.original_file = original_file

        self.database_folder = database_folder
        self.original_size = original_size
        self.import_date = import_date
        self.modify_date = modify_date
        self.edited = edited
        self.owner = owner
        self.export = export
        self.orientation = orientation
        self.rename = rename
        self.full_path = self.folder_with_filename()
        self.latitude = latitude
        self.longitude = longitude

    def update_thumbnail(self):
        thumbnail = self.__generate_thumbnail()
        self.thumbnail = sqlite3.Binary(thumbnail)

    def folder_name(self):
        date_info = datetime.fromtimestamp(self.original_date)
        return naming('<%Y-%M-%D>', title=self.original_file, year=date_info.year, month=date_info.month,
                      day=date_info.day)

    def folder_with_filename(self):
        date_info = datetime.fromtimestamp(self.original_date)
        return naming('%Y-%M-%D/%T>', title=self.original_file, year=date_info.year, month=date_info.month,
                      day=date_info.day)

    def new_full_filename(self, import_to):
        return os.path.join(import_to, self.folder_with_filename())

    def old_full_filename(self):
        return os.path.join(self.database_folder, self.original_file)

    def get_lat_lon4(self, gps_latitude_ref, gps_latitude, gps_longitude_ref, gps_longitude):
        """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
        lat = None
        lon = None

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = self._convert_to_degress(gps_latitude)
            if gps_latitude_ref != "N":
                lat = 0 - lat

            lon = self._convert_to_degress(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon

        return lat, lon

    def _convert_to_degress(self, value):
        """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
        d0 = value[0][0]
        d1 = value[0][1]
        d = float(d0) / float(d1)

        m0 = value[1][0]
        m1 = value[1][1]
        m = float(m0) / float(m1)

        s0 = value[2][0]
        s1 = value[2][1]
        s = float(s0) / float(s1)

        return d + (m / 60.0) + (s / 3600.0)

    def _get_if_exist(self, data, key):
        if key in data:
            return data[key]

        return None

    def __generate_thumbnail(self):
        """Creates a thumbnail image for a photo.

        Arguments:
            fullpath: Path to file, relative to the screenDatabase folder.
            database_folder: Database root folder where the file is.
        Returns:
            A thumbnail jpeg
        """
        app = App.get_running_app()
        full_filename = self.old_full_filename()
        thumbnail = ''
        extension = os.path.splitext(full_filename)[1].lower()

        try:
            if extension in imagetypes:
                # This is an image file, use PIL to generate a thumnail
                image = Image.open(full_filename)
                image.thumbnail((app.thumbsize, app.thumbsize), Image.ANTIALIAS)
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

                image = Image.frombuffer(mode='RGB', size=(frame_size[0], frame_size[1]), data=image_data,
                                         decoder_name='raw')
                image = image.transpose(1)

                image.thumbnail((app.thumbsize, app.thumbsize), Image.ANTIALIAS)
                output = BytesIO()
                image.save(output, 'jpeg')
                thumbnail = output.getvalue()
            return thumbnail
        except Exception as e:
            print(e)
            return None


class Tag(Base,BaseModel):
    __tablename__ = 'tag'

    id = Column(Integer, Sequence('tag_id_seq'), primary_key=True)
    name = Column(String)

    photos = relationship('Photo', secondary=photos_tags, back_populates='tags')

    can_delete_folder = True
    can_new_folder = True
    can_rename_folder = True

    def __repr__(self):
        return "<Tag( id='%s', name='%s')>" % (
            self.id, self.name)

    def delete(self):
        app = App.get_running_app()
        app.session.delete(self)
        app.session.commit()

    def create_table(engine):
        Tag.__table__
        Base.metadata.create_all(engine)


class Folder(Base,BaseModel):
    __tablename__ = 'folder'

    id = Column(Integer, Sequence('folder_id_seq'), primary_key=True)
    name = Column(String)
    title = Column(Integer)
    description = Column(Integer)
    nb_photos = Column(Integer, default=0)
    can_delete_folder = True
    photos = relationship('Photo', order_by=Photo.rename, back_populates='folder')
    fullname = 'F1234'

    def __repr__(self):
        return "<Folder( id='%s',name='%s', title='%s', description='%s')>" % (
            self.id, self.name, self.title, self.description)

    def create_table(engine):
        Folder.__table__
        Base.metadata.create_all

#      FOLDER *************************
#  def by_id(self,id):
#    cmd = 'select * from folders where id = %d limit 1' % int(id)
#    folders = list(self.database.execute(cmd))
#    if folders:
#      return folders[0]
#    return None
#
#  def create_or_find(self,folder_path):
#    folder_path = agnostic_path(folder_path)
#    folder = self.exist(folder_path)
#    if not folder:
#
#      cmd = "insert into folders (Path) values (\"%s\")" % folder_path
#      res = self.database.execute(cmd)
#      self.commit()
#      folder = self.exist(folder_path)
#      self.create_folder_directory(folder_path)
#    return folder
#
#  def exist(self,fullpath):
#    if not isinstance(fullpath, str):
#      raise ValueError('fullpath must be a string', fullpath)
#
#    filename_matches = list(self.database.execute('SELECT * FROM folders WHERE path = ?', (fullpath,)))
#    if filename_matches:
#          return filename_matches[0]
#    return False
#
#  #rename_folder
#  def rename(self, old_folder_path, new_name):
#        """Rename a folder in place.  Uses the self.move_folder function.
#        Arguments:
#            old_folder_path: String, path of the folder to rename.
#            new_name: String, new name for the folder.
#        """
#        raise ValueError('Not sure we should enable rename folder')
#
#        folder_path, old_name = os.path.split(old_folder_path)
#        self.move_folder(old_folder_path, folder_path, rename=new_name)
#
#  def create_folder_directory(self, _path):
#    """Attempts to create a new folder in every screenDatabase directory.
#    Argument:
#        folder: String, the folder path to create.  Must be screenDatabase-relative.
#    """
#
#    databases = self.app.get_database_directories()
#    created = False
#    for database in databases:
#      try:
#        if not os.path.isdir(os.path.join(database, _path)):
#          os.makedirs(os.path.join(database, _path))
#          created = True
#      except:
#        pass
#    if created:
#      self.app.message("Created the folder '" + _path + "'")
#
#  def delete(self, folder):
#    """Delete a folder and all photos within it.  Removes the contained photos from the screenDatabase as well.
#    Argument:
#        folder: String, the folder to be deleted.  Must be a screenDatabase-relative path.
#    """
#    raise ValueError('Must fix it')
#    folders = []
#    update_folders = []
#    databases = self.get_database_directories()
#
#    deleted_photos = 0
#    deleted_folders = 0
#
#    # Detect all folders to delete
#    for database in databases:
#      full_folder = os.path.join(database, folder)
#      if os.path.isdir(full_folder):
#        folders.append([database, folder])
#      found_folders = list_folders(full_folder)
#      for found_folder in found_folders:
#        folders.append([database, os.path.join(folder, found_folder)])
#
#    # Delete photos from folders
#    for found_path in folders:
#      database, folder_name = found_path
#      photos = self.Photo.by_folder(folder_name)
#      if photos:
#        update_folders.append(folder_name)
#      for photo in photos:
#        photo_path = os.path.join(photo[2], photo[0])
#        deleted = self.Photo.delete_file(photo[0], photo_path)
#        if not deleted:
#          break
#        deleted_photos = deleted_photos + 1
#
#    # Delete folders
#    for found_path in folders:
#      database, folder_name = found_path
#      full_found_path = os.path.join(database, folder_name)
#      try:
#        rmtree(full_found_path)
#        deleted_folders = deleted_folders + 1
#      except:
#        pass
#    self.Photo.deleteFolder(folder)
#
#    if deleted_photos or deleted_folders:
#      self.message("Deleted " + str(deleted_photos) + " photos and " + str(deleted_folders) + " folders.")
#
#
#
#  def delete_folder(self,folder):
#    self.database.execute('DELETE FROM folders WHERE path = ?', (agnostic_path(folder),))
#    self.commit()
#
#  def get_folder_treeview_info(self):
#      folders = []
#      folder_items = list(self.database.execute('SELECT * FROM folders'))
#      for item in folder_items:
#        folders.append([local_path(item[Folder.PATH]),item[Folder.TITLE],item[Folder.DESCRIPTION]])
#      return folders
#
#  def folders(self):
#    folders_out = []
#    folder_items = list(self.app.Photo.select('SELECT * FROM folders'))
#    for item in folder_items:
#      folders_out.append(local_path(item[Folder.PATH]))
#    return folders_out
#
#  def insert(self,folderinfo):
#    path, title, description = folderinfo
#    renamed_path = agnostic_path(path)
#    self.database.execute("insert into folders values(?, ?, ?)", (renamed_path, title, description))
#    return self
#
#  def update_title(self,id,title):
#    self.database.execute("UPDATE folders SET Title = ? WHERE id = ?", (title, id,))
#    self.commit()
#
#  def update_description(self,id, description):
#    self.database.execute("UPDATE folders SET Description = ? WHERE id = ?", (description, id,))
#    self.commit()
#
#  def update(self,folderinfo):
#    path, title, description = folderinfo
#    renamed_path = agnostic_path(path)
#    self.database.execute("UPDATE folders SET Title = ?, Description = ? WHERE Path = ?",
#                         (title, description, renamed_path,))
#    self.commit()
#
#


# Photo *******
# def insert(self, folderId, full_filename, fileinfo):
#   """Add a new photo to the screenDatabase.
#   Argument:
#       fileinfo: List, a photoinfo object.
#   """
#   thumbnail = self.__generate_thumbnail(local_path(full_filename))
#   thumbnail = sqlite3.Binary(thumbnail)
#
#   self.database.execute("insert into photos(FullPath, FolderId, DatabaseFolder, OriginalDate, OriginalSize, Rename, ImportDate, ModifiedDate,  Edited, Orientation, Thumbnail) values(?,?,?,?,?,?,?,?,?,?,?)",(
#   fileinfo.fullpath, folderId, fileinfo.database_folder, fileinfo.original_date, fileinfo.original_size[0],
#   fileinfo.rename, fileinfo.import_date, fileinfo.modify_date, fileinfo.edited, fileinfo.orientation, thumbnail))
#   self.commit()
#
# def update(self, fileinfo):
#   """Updates a photo's screenDatabase entry with new info.
#   Argument:
#       fileinfo: List, a photoinfo object.
#   """
#
#   fileinfo = agnostic_photoinfo(fileinfo)
#   self.database.execute(
#     "UPDATE photos SET Rename = ?, ModifiedDate = ?,  Edited = ?, Orientation = ?, Persons = ? WHERE FullPath = ?",
#     (
#       fileinfo[Photo.RENAME],
#       fileinfo[Photo.MODIFYDATE],
#       fileinfo[Photo.EDITED],
#       fileinfo[Photo.ORIENTATION],
#       fileinfo[Photo.FULLPATH]))
#   self.commit()
#
# def move(self, fileinfo):
#       """Updates a photo's screenDatabase folder.
#       Argument:
#           fileinfo: list, a photoinfo object.
#       """
#
#       fileinfo = agnostic_photoinfo(fileinfo)
#       self.database.execute("UPDATE photos SET DatabaseFolder = ? WHERE FullPath = ?", (fileinfo[Photo.DATABASEFOLDER], fileinfo[Photo.FULLPATH]))
#
#
# def thumbnail(self,fullpath,temporary=False):
#   fullpath = agnostic_path(fullpath)
#   thumbnail = self.database.execute('SELECT * FROM photos WHERE FullPath = ?', (fullpath,))
#
#   thumbnail = list(thumbnail)
#   if thumbnail:
#     thumbnail = local_thumbnail(list(thumbnail[Photo.THUMBNAIL]))
#   return thumbnail
#
# def thumbnail_write(self, fullpath, modify_date, thumbnail, orientation, temporary=False):
#       """Save or updates a thumbnail to the thumbnail screenDatabase.
#       Arguments:
#           fullpath: String, screenDatabase-relative path to the photo.
#           modify_date: Integer, the modified date of the original photo file.
#           thumbnail: Thumbnail image data.
#           orientation: Integer, EXIF orientation code.
#           temporary: Boolean, if True, save to the temporary thumbnails screenDatabase.
#       """
#       fullpath = agnostic_path(fullpath)
#       self.database.execute("UPDATE photos SET ModifiedDate = ?, Thumbnail = ?, Orientation = ? WHERE FullPath = ?", (modify_date, thumbnail, orientation, fullpath, ))
#
# def thumbnail_update(self, fullpath, database, modify_date, orientation, temporary=False, force=False):
#   """Check if a thumbnail is already in screenDatabase, check if out of date, update if needed.
#   Arguments:
#       fullpath: String, the screenDatabase-relative path to the photo.
#       database: String, screenDatabase directory the photo is in.
#       modify_date: Integer, the modified date of the original photo.
#       orientation: Integer, EXIF orientation code.
#       temporary: Boolean, if True, uses the temporary thumbnails screenDatabase.
#       force: Boolean, if True, will always update thumbnail, regardless of modified date.
#   Returns: Boolean, True if thumbnail updated, False if not.
#   """
#
#   # check if thumbnail is already in screenDatabase, check if out of date, update if needed
#   matches = self.thumbnail(fullpath, temporary=temporary)
#   if matches:
#     if modify_date <= matches[1] and not force:
#       return False
#   thumbnail = self.__generate_thumbnail(local_path(fullpath), local_path(database))
#   thumbnail = sqlite3.Binary(thumbnail)
#   self.Photo.thumbnail_write(fullpath=fullpath, modify_date=modify_date, thumbnail=thumbnail,
#                              orientation=orientation, temporary=temporary)
#   return True
#
# #database_get_folder
# def by_folder_id(self, folder_id):
#   """Get photos in a folder.
#   Argument:
#       folder: String, screenDatabase-relative folder name to get.
#   Returns: List of photoinfo Lists.
#   """
#
#   # if database:
#   #   database = agnostic_path(database)
#   #   photos = list(
#   #     self.database.execute('SELECT * FROM photos WHERE Folder = ? AND DatabaseFolder = ?', (folder, database,)))
#   # else:
#   cmd = "select * from photos where FolderId = %d" % int(folder_id)
#   photos = list(self.database.execute(cmd))
#   return local_paths(photos)
#
#
# def find_by_fullpath(self,fullpath):
#   fullpath = agnostic_path(fullpath)
#   photo = self.database.execute('SELECT * FROM photos WHERE FullPath = ?', (fullpath,))
#   photo = list(photo)
#   if photo:
#     photo = list(photo[0])
#     photo[0] = local_path(photo[0])
#   return photo
#
# def exist(self,fullpath):
#   if not isinstance(fullpath,str):
#     raise ValueError('filepath must be of type string',fullpath)
#
#   filename_matches = list(self.database.execute('SELECT * FROM photos WHERE fullpath = ?', (fullpath,)))
#   if filename_matches:
#     return filename_matches[0]
#   return False
#
# def delete_folder(self,folder):
#   self.database.execute('DELETE FROM photos WHERE folder = ?', (agnostic_path(folder),))
#   self.commit()
#
# # def get_folder_treeview_info(self):
# #     folders = []
# #     folder_items = list(self.database.execute('SELECT * FROM photos'))
# #     for item in folder_items:
# #       folders.append([local_path(item[Photo.FOLDER]),'',''])  #title, description
# #     return folders
#
# def folders(self):
#   folders_out = []
#   folder_items = list(self.database.execute('SELECT distinct(fullpath) FROM photos'))
#   for item in folder_items:
#     folders_out.append(local_path(item[0]))
#   return folders_out
#
# def folder_exist(self,folder):
#   folder = agnostic_path(folder)
#   matches = self.database.execute('SELECT * FROM photos WHERE folder = ?', (folder,))
#   matches = list(matches)
#   if matches:
#     matches = list(matches[0])
#     matches[0] = local_path(matches[0])
#   return matches
#
# def delete_by_fullpath(self,fullpath):
#   fullpath = agnostic_path(fullpath)
#   self.database.execute('DELETE FROM photos WHERE FullPath = ?', (fullpath,))
#
#
# def delete_file(self, fullpath, filename, message=False):
#   """Deletes a photo file, and removes it from the screenDatabase.
#   Arguments:
#       fullpath: String, screenDatabase identifier for the photo to delete.
#       filename: Full path to the photo to delete.
#       message: Display an app message that the file was deleted.
#   """
#
#   photoinfo = self.exist(fullpath)
#   if os.path.isfile(filename):
#     deleted = self.app.delete_file(filename)
#   else:
#     deleted = True
#   if deleted is True:
#     if os.path.isfile(photoinfo[10]):
#       self.app.delete_file(photoinfo[10])
#
#     self.Photo.delete_by_fullpath(fullpath)
#     if message:
#       self.app.message("Deleted the file '" + filename + "'")
#     return True
#   else:
#     if message:
#       self.app.popup_message(text='Could not delete file', title='Warning')
#     return deleted
#
# def rename(self, fullpath, newname, newfolder, dontcommit=False):
#       """Changes the screenDatabase-relative path of a photo to another path.
#       Updates both photos and thumbnails databases.
#       Arguments:
#           fullpath: String, the original screenDatabase-relative path.
#           newname: String, the new screenDatabase-relative path.
#           newfolder: String, new screenDatabase-relative containing folder for the file.
#           dontcommit: Dont write to the screenDatabase when finished.
#       """
#
#       fullpath = agnostic_path(fullpath)
#       newname = agnostic_path(newname)
#       if self.exist(newname):
#           self.delete_by_fullpath(newname)
#
#       newfolder_rename = agnostic_path(newfolder)
#       self.database.execute("UPDATE photos SET FullPath = ?, Folder = ? WHERE FullPath = ?", (newname, newfolder_rename, fullpath, ))
#       if not dontcommit:
#           self.commit()
#
#
# def clean(self,deep=False):
#   databases = self.app.get_database_directories()
#
#   # remove referenced files if the screenDatabase that contained them is no longer loaded
#   found_databases = list(self.database.execute('SELECT DatabaseFolder FROM photos GROUP BY DatabaseFolder'))
#   for database in found_databases:
#     if local_path(database[0]) not in databases:
#       self.database.execute('DELETE FROM photos WHERE DatabaseFolder = ?', (database[0],))
#
#   # remove references if the photos are not found
#   for database in databases:
#     if os.path.isdir(database) or deep:
#       database_renamed = agnostic_path(database)
#       photos = list(self.database.execute('SELECT * FROM photos WHERE DatabaseFolder = ?', (database_renamed,)))
#       for photo in photos:
#         photo_file = os.path.join(local_path(photo[2]), local_path(photo[0]))
#         if not isfile2(photo_file):
#           self.Photo.delete_by_fullpath(photo[Photo.FULLPATH])
#
#


# TAGS ***************************
# #tag_make
# def create(self, tag_name):
#   """Create a new photo tag.
#   Argument:
#       tag_name: String, name of the tag to create.
#   """
#   cmd = "insert into tags (Name) values ('%s')" % tag_name
#   self.database.execute(cmd)
#   self.commit()
#
# #remove_tag
# def delete(self, tag):
#   """Deletes a tag.
#   Argument:
#       tag: String, the tag to be deleted."""
#   self.database.execute('DELETE FROM tags WHERE name = ?',tag)
#   self.database.execute('DELETE FROM photos_tags where name = ?', tag)  # must fix it
#   raise ValueError('must fix delet tag')
#
#
# def toggle(self, fullpath, tag):
#   """Toggles a tag on a photo.  Used for enabling/disabling the 'favorite' tag.
#   Arguments:
#       fullpath: String, the screenDatabase-relative path to the photo.
#       tag: String, the tag to be toggled.
#   """
#   raise ValueError('fix tag toggle')
#   tag = tag.lower().strip(' ')
#   fullpath = agnostic_path(fullpath)
#   info = self.photos.select('SELECT * FROM photos WHERE FullPath = ?', (fullpath,))
#   info = list(info)
#   if info:
#     info = list(info[0])
#     tags_unformatted = info[8].strip(' ')
#     original_tags = tags_unformatted.split(',')
#     if tag in original_tags:
#       original_tags.remove(tag)
#     else:
#       original_tags.append(tag)
#     new_tags = ",".join(original_tags)
#     info[8] = new_tags
#     self.app.Photo.update(info)
#     self.update_photoinfo(folders=info[1])
#
# def all(self):
#   tags = list(self.database.execute('SELECT * FROM tags;'))
#   return tags
#
# def photos(self, tag):
#   """Gets all photos that have a tag applied to them.
#   Argument:
#       tag: String, the tag to search for.
#   Returns:
#       List of photoinfo Lists.
#   """
#   photos = self.database.execute('SELECT photos.* FROM ((photos inner join tags_photos on photos.id = tags_photos.PhotoId) inner join tags on tags_photos.TagId = tags.Id) where tags.name = ?;', (tag,))
#   photos = list(photos)
#   return local_paths(photos)
#
# def add(self, fullpath, tag):
#   """Adds a tag to a photo.
#   Arguments:
#       fullpath: String, the screenDatabase-relative path to the photo.
#       tag: String, the tag to be added.
#   """
#   raise ValueError('must fix Tag.add')
#   # tag = tag.lower().strip(' ')
#   # fullpath = agnostic_path(fullpath)
#   # info = self.photos.select('SELECT * FROM photos WHERE FullPath = ?', (fullpath,))
#   # info = list(info)
#   # if info:
#   #   info = list(info[0])
#   #   original_tags = info[8].split(',')
#   #   current_tags = []
#   #   update = False
#   #   for original in original_tags:
#   #     if original.strip(' '):
#   #       current_tags.append(original)
#   #     else:
#   #       update = True
#   #   if tag not in current_tags:
#   #     current_tags.append(tag)
#   #     update = True
#   #   if update:
#   #     new_tags = ",".join(current_tags)
#   #     info[8] = new_tags
#   #     self.app.Photo.update(info)
#   #     self.update_photoinfo(folders=info[1])
#   #     return True
#   return False
#
# def remove(self, fullpath,tag,message):
#   # remove a tag to a photo
#   raise ValueError('remove tag to fix')
#
#   # tag = tag.lower()
#   #     fullpath = agnostic_path(fullpath)
#   #     info = self.Phophotos.select('SELECT * FROM photos WHERE FullPath = ?', (fullpath, ))
#   #     info = list(info)
#   #     if info:
#   #         info = list(info[0])
#   #         current_tags = info[8].split(',')
#   #         if tag in current_tags:
#   #             current_tags.remove(tag)
#   #             new_tags = ",".join(current_tags)
#   #             info[8] = new_tags
#   #             self.app.Photo.update(info)
#   #             self.update_photoinfo(folders=info[1])
#   #             if message:
#   #                 self.message("Removed tag '"+tag+"' from the photo.")
#
#
#     self.database.execute('''CREATE TABLE IF NOT EXISTS tags_photos(
#                                     TagId integer not null,
#                                     PhotoId integer not null);''')
#
#     self.database.execute('''
#       CREATE INDEX "tag_Name" ON "tags" ("Name");
#     ''')
#
#     self.database.execute('''
#       CREATE INDEX "tag_TagId" ON "tags_photos" ("TagId");
#     ''')
#
#     self.database.execute('''
#      CREATE INDEX "tag_PhotoId" ON "tags_photos" ("PhotoId");
#    ''')
