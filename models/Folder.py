
import os
from generalcommands import agnostic_path, local_path, agnostic_photoinfo
from models.Database import Database


class Folder(Database):
  ID=0
  PATH=1
  TITLE=2
  DESCRIPTION=3


  def __init__(self,app,database):
    super(Folder,self).__init__(app=app,database=database)
    self.__create()

  def all(self):
    return  list(self.database.execute('select * from folders order by path DESC'))

  def by_id(self,id):
    cmd = 'select * from folders where id = %d limit 1' % int(id)
    folders = list(self.database.execute(cmd))
    if folders:
      return folders[0]
    return None

  def create_or_find(self,folder_path):
    folder_path = agnostic_path(folder_path)
    folder = self.exist(folder_path)
    if not folder:

      cmd = "insert into folders (Path) values (\"%s\")" % folder_path
      res = self.database.execute(cmd)
      self.commit()
      folder = self.exist(folder_path)
      self.create_folder_directory(folder_path)
    return folder

  def exist(self,fullpath):
    if not isinstance(fullpath, str):
      raise ValueError('fullpath must be a string', fullpath)

    filename_matches = list(self.database.execute('SELECT * FROM folders WHERE path = ?', (fullpath,)))
    if filename_matches:
          return filename_matches[0]
    return False

  #rename_folder
  def rename(self, old_folder_path, new_name):
        """Rename a folder in place.  Uses the self.move_folder function.
        Arguments:
            old_folder_path: String, path of the folder to rename.
            new_name: String, new name for the folder.
        """
        raise ValueError('Not sure we should enable rename folder')

        folder_path, old_name = os.path.split(old_folder_path)
        self.move_folder(old_folder_path, folder_path, rename=new_name)

  def create_folder_directory(self, _path):
    """Attempts to create a new folder in every screenDatabase directory.
    Argument:
        folder: String, the folder path to create.  Must be screenDatabase-relative.
    """

    databases = self.app.get_database_directories()
    created = False
    for database in databases:
      try:
        if not os.path.isdir(os.path.join(database, _path)):
          os.makedirs(os.path.join(database, _path))
          created = True
      except:
        pass
    if created:
      self.app.message("Created the folder '" + _path + "'")

  def delete(self, folder):
    """Delete a folder and all photos within it.  Removes the contained photos from the screenDatabase as well.
    Argument:
        folder: String, the folder to be deleted.  Must be a screenDatabase-relative path.
    """
    raise ValueError('Must fix it')
    folders = []
    update_folders = []
    databases = self.get_database_directories()

    deleted_photos = 0
    deleted_folders = 0

    # Detect all folders to delete
    for database in databases:
      full_folder = os.path.join(database, folder)
      if os.path.isdir(full_folder):
        folders.append([database, folder])
      found_folders = list_folders(full_folder)
      for found_folder in found_folders:
        folders.append([database, os.path.join(folder, found_folder)])

    # Delete photos from folders
    for found_path in folders:
      database, folder_name = found_path
      photos = self.Photo.by_folder(folder_name)
      if photos:
        update_folders.append(folder_name)
      for photo in photos:
        photo_path = os.path.join(photo[2], photo[0])
        deleted = self.Photo.delete_file(photo[0], photo_path)
        if not deleted:
          break
        deleted_photos = deleted_photos + 1

    # Delete folders
    for found_path in folders:
      database, folder_name = found_path
      full_found_path = os.path.join(database, folder_name)
      try:
        rmtree(full_found_path)
        deleted_folders = deleted_folders + 1
      except:
        pass
    self.Photo.deleteFolder(folder)

    if deleted_photos or deleted_folders:
      self.message("Deleted " + str(deleted_photos) + " photos and " + str(deleted_folders) + " folders.")



  def delete_folder(self,folder):
    self.database.execute('DELETE FROM folders WHERE path = ?', (agnostic_path(folder),))
    self.commit()

  def get_folder_treeview_info(self):
      folders = []
      folder_items = list(self.database.execute('SELECT * FROM folders'))
      for item in folder_items:
        folders.append([local_path(item[Folder.PATH]),item[Folder.TITLE],item[Folder.DESCRIPTION]])
      return folders

  def folders(self):
    folders_out = []
    folder_items = list(self.app.Photo.select('SELECT * FROM folders'))
    for item in folder_items:
      folders_out.append(local_path(item[Folder.PATH]))
    return folders_out

  def insert(self,folderinfo):
    path, title, description = folderinfo
    renamed_path = agnostic_path(path)
    self.database.execute("insert into folders values(?, ?, ?)", (renamed_path, title, description))
    return self

  def update_title(self,id,title):
    self.database.execute("UPDATE folders SET Title = ? WHERE id = ?", (title, id,))
    self.commit()

  def update_description(self,id, description):
    self.database.execute("UPDATE folders SET Description = ? WHERE id = ?", (description, id,))
    self.commit()

  def update(self,folderinfo):
    path, title, description = folderinfo
    renamed_path = agnostic_path(path)
    self.database.execute("UPDATE folders SET Title = ?, Description = ? WHERE Path = ?",
                         (title, description, renamed_path,))
    self.commit()

  def __create(self):
    try:
      self.database.execute('select * from folders')
    except:
      self.database.execute('''CREATE TABLE IF NOT EXISTS folders(
                                 Id integer primary key autoincrement ,
                                 Path text not null unique,
                                 Title text,
                                 Description text);''')

      self.database.execute('''
          CREATE INDEX "folder_Path" ON "folders" ("Path");
        ''')
