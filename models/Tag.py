from models.Database import Database
from generalcommands import agnostic_path, local_paths

class Tag(Database):
  ID=0
  NAME=1

  TAGID=0
  PHOTOID=1

  def __init__(self,app,database):
    super(Tag,self).__init__(app=app,database=database)
    self.__create()

  #tag_make
  def create(self, tag_name):
    """Create a new photo tag.
    Argument:
        tag_name: String, name of the tag to create.
    """
    cmd = "insert into tags (Name) values ('%s')" % tag_name
    self.database.execute(cmd)
    self.commit()

  #remove_tag
  def delete(self, tag):
    """Deletes a tag.
    Argument:
        tag: String, the tag to be deleted."""
    self.database.execute('DELETE FROM tags WHERE name = ?',tag)
    self.database.execute('DELETE FROM photos_tags where name = ?', tag)  # must fix it
    raise ValueError('must fix delet tag')


  def toggle(self, fullpath, tag):
    """Toggles a tag on a photo.  Used for enabling/disabling the 'favorite' tag.
    Arguments:
        fullpath: String, the screenDatabase-relative path to the photo.
        tag: String, the tag to be toggled.
    """
    raise ValueError('fix tag toggle')
    tag = tag.lower().strip(' ')
    fullpath = agnostic_path(fullpath)
    info = self.photos.select('SELECT * FROM photos WHERE FullPath = ?', (fullpath,))
    info = list(info)
    if info:
      info = list(info[0])
      tags_unformatted = info[8].strip(' ')
      original_tags = tags_unformatted.split(',')
      if tag in original_tags:
        original_tags.remove(tag)
      else:
        original_tags.append(tag)
      new_tags = ",".join(original_tags)
      info[8] = new_tags
      self.app.Photo.update(info)
      self.update_photoinfo(folders=info[1])

  def all(self):
    tags = list(self.database.execute('SELECT * FROM tags;'))
    return tags

  def photos(self, tag):
    """Gets all photos that have a tag applied to them.
    Argument:
        tag: String, the tag to search for.
    Returns:
        List of photoinfo Lists.
    """
    photos = self.database.execute('SELECT photos.* FROM ((photos inner join tags_photos on photos.id = tags_photos.PhotoId) inner join tags on tags_photos.TagId = tags.Id) where tags.name = ?;', (tag,))
    photos = list(photos)
    return local_paths(photos)

  def add(self, fullpath, tag):
    """Adds a tag to a photo.
    Arguments:
        fullpath: String, the screenDatabase-relative path to the photo.
        tag: String, the tag to be added.
    """
    raise ValueError('must fix Tag.add')
    # tag = tag.lower().strip(' ')
    # fullpath = agnostic_path(fullpath)
    # info = self.photos.select('SELECT * FROM photos WHERE FullPath = ?', (fullpath,))
    # info = list(info)
    # if info:
    #   info = list(info[0])
    #   original_tags = info[8].split(',')
    #   current_tags = []
    #   update = False
    #   for original in original_tags:
    #     if original.strip(' '):
    #       current_tags.append(original)
    #     else:
    #       update = True
    #   if tag not in current_tags:
    #     current_tags.append(tag)
    #     update = True
    #   if update:
    #     new_tags = ",".join(current_tags)
    #     info[8] = new_tags
    #     self.app.Photo.update(info)
    #     self.update_photoinfo(folders=info[1])
    #     return True
    return False

  def remove(self, fullpath,tag,message):
    # remove a tag to a photo
    raise ValueError('remove tag to fix')

    # tag = tag.lower()
    #     fullpath = agnostic_path(fullpath)
    #     info = self.Phophotos.select('SELECT * FROM photos WHERE FullPath = ?', (fullpath, ))
    #     info = list(info)
    #     if info:
    #         info = list(info[0])
    #         current_tags = info[8].split(',')
    #         if tag in current_tags:
    #             current_tags.remove(tag)
    #             new_tags = ",".join(current_tags)
    #             info[8] = new_tags
    #             self.app.Photo.update(info)
    #             self.update_photoinfo(folders=info[1])
    #             if message:
    #                 self.message("Removed tag '"+tag+"' from the photo.")

  def __create(self):
    try:
      self.database.execute('select * from tags')
    except:
      self.database.execute('''CREATE TABLE IF NOT EXISTS tags(
                                      Id integer not null primary key autoincrement unique,
                                      Name text);''')

      self.database.execute('''CREATE TABLE IF NOT EXISTS tags_photos(
                                      TagId integer not null,
                                      PhotoId integer not null);''')

      self.database.execute('''
        CREATE INDEX "tag_Name" ON "tags" ("Name");
      ''')

      self.database.execute('''
        CREATE INDEX "tag_TagId" ON "tags_photos" ("TagId");
      ''')

      self.database.execute('''
       CREATE INDEX "tag_PhotoId" ON "tags_photos" ("PhotoId");
     ''')
