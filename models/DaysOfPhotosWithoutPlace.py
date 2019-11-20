from kivy.app import App
from models.BaseModel import BaseModel
from models.PhotosTags import Country
from TreeViewItem.TreeViewItem import TreeViewItem
from models.Folders import Folders
from models.PhotosTags import Folder
from models.PhotosTags import Photo

class DaysOfPhotosWithoutPlace(BaseModel):
    name = 'Photo with no places'
    photos = []

    def daysWithNbPhotos(self):
        app = App.get_running_app()
        return app.session.execute('select folder.id,folder.name, count(*) from folder inner join photo on folder.id = photo.folder_id where photo.place_id is null group by folder.name order by folder.name desc')




