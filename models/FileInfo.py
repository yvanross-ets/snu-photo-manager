import os
import time
from datetime import datetime,date
from PIL import Image


from generalcommands import list_files, format_size, naming
from generalconstants import naming_method_default

try:
    from configparser import ConfigParser
except:
    from six.moves import configparser

class FileInfo():
  file_info = None
  import_mode = None
  modified_date=None
  fullpath = None
  folder = None
  database_folder = None
  original_date = None
  original_size = None
  import_date = None
  modified_date = None
  tags = None
  edited = None
  original_file = None
  owner = None
  export = None
  orientation = None
  rename = None

  def __init__(self,file_info, import_mode=False, modified_date=False):
    """Reads a photo file and determines all the basic information about it.
          Will attempt to read info files generated by Google's Picasa or by this program, other information is read directly
          from the file.

          Arguments:
              file_info: A list containing file information:
                  Relative path to the file from the screenDatabase directory
                  Database root directory
              import_mode: When reading the file from a camera or other import source, don't try to find any info files.
              modified_date: if this is already found, can be passed in to save time

          Returns: None
       """
    self.file_info = file_info
    self.import_mode = import_mode
    self.modified_date = modified_date
    self.__extractPhotoInfo()

  def __extractPhotoInfo(self):

    filepath, filename = os.path.split(self.file_info[0])
    database_folder = self.file_info[1]
    full_folder = os.path.join(database_folder, filepath)
    full_filename = os.path.join(full_folder, filename)
    full_folder = os.path.join(database_folder, filepath)
    original_file = filename
    original_date = int(os.path.getmtime(full_filename))
    original_size = int(os.path.getsize(full_filename))
    import_date = int(time.time() - time.timezone)
    orientation = 0

    if not self.modified_date:
      modified_date = int(os.path.getmtime(full_filename))

    tags = ''
    edited = 0
    owner = ''
    export = 1
    rename = filename

    if not self.import_mode:
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
            tags = 'favorite'
        except:
          pass

      infofile = os.path.join(full_folder, '.photoinfo.ini')
      if os.path.isfile(infofile):
        configfile = ConfigParser(interpolation=None)
        try:
          configfile.read(infofile)
          configitems = dict(configfile.items(filename))
          if 'tags' in configitems:
            tags = configitems['tags']
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
      orientation = 1
      try:
        exif_tag = Image.open(full_filename)._getexif()
        if 274 in exif_tag:
          orientation = exif_tag[274]
        if 36867 in exif_tag:
          original_exif_date = exif_tag[36867]
          extracted_date = datetime.strptime(original_exif_date, '%Y:%m:%d  %H:%M:%S')
          original_date = extracted_date.timestamp()
          print(original_exif_date,original_date)
          print("test")
      except Exception as e:
        print("ERROR:",e)
        pass

    # always set original_date and original_file before calling new_folder_name
    self.original_date = original_date
    self.original_file = original_file

    self.database_folder = database_folder
    self.original_size = original_size,
    self.import_date = import_date
    self.modified_date = modified_date
    self.tags = tags
    self.edited = edited
    self.owner = owner
    self.export = export
    self.orientation = orientation
    self.rename = rename
    self.folder = self.new_folder_name()
    self.fullpath = self.new_folder_with_filename()

  def photoInfo(self):
    return [
    self.fullpath,
    self.folder,
    self.database_folder,
    self.original_date,
    self.original_size,
    self.import_date,
    self.modified_date,
    self.tags,
    self.edited,
    self.original_file,
    self.owner,
    self.export,
    self.orientation,
    ]


  def new_folder_name(self):
    date_info = datetime.fromtimestamp(self.original_date)
    return naming('<%Y-%M-%D>', title=self.original_file, year=date_info.year, month=date_info.month,
                  day=date_info.day)

  def new_folder_with_filename(self):
    date_info = datetime.fromtimestamp(self.original_date)
    return naming('%Y-%M-%D/%T>',title=self.original_file, year=date_info.year, month=date_info.month, day=date_info.day)

  def new_full_filename(self,import_to):
    return os.path.join(import_to,self.new_folder_with_filename())


  def old_full_filename(self):
        return os.path.join(self.file_info[1],self.file_info[0])






