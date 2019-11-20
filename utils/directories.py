import os, sys

def removeEmptyFolders(path, removeRoot=True):
  'Function to remove empty folders'
  if not os.path.isdir(path):
    return False

  directory_removed = False
  # remove empty subfolders
  files = os.listdir(path)
  if len(files):
    for f in files:
      fullpath = os.path.join(path, f)
      if os.path.isdir(fullpath):
        removeEmptyFolders(fullpath)

  # if folder empty, delete it
  files = os.listdir(path)
  #sudo find / -name “.DS_Store” -depth - exec rm {} \;

  if (len(files) == 0 or ( len(files) == 1 and files[0] == '.DS_Store')) and removeRoot:
    if len(files) == 1 and files[0] == '.DS_Store':
      os.remove(os.path.join(path,files[0]))

    print("Removing empty folder:", path)
    directory_removed = True
    os.rmdir(path)

  return directory_removed
