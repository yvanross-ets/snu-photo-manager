class BaseModel:
    can_new_folder = False
    can_rename_folder = False
    can_delete_folder = False


    def delete(self):
        raise NotImplementedError('Must implement delete method  to use this base class')
