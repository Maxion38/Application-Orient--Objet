from gui import FolderSelectorApp
from kivy.config import Config
import os

if __name__ == '__main__':
    Config.set('graphics', 'width', '550')
    Config.set('graphics', 'height', '200')

    f1 = FolderSelectorApp()
    f1.run()
    f1 = FolderSelectorApp()
    print(os.path.normpath(f1.selected_folder))