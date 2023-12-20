from kivy.app import App
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
import tkinter as tk
from tkinter import filedialog
import os
from programme import run_program


class FolderSelectorApp(App):
    def __init__(self, **kwargs):
        super(FolderSelectorApp, self).__init__(**kwargs)
        self.selected_folder = "Veuillez selectionner un dossier"


    def build(self):
        self.title = "Fancy storage"

        # Select and run
        select_dir = BoxLayout(orientation='horizontal')
        select_dir.add_widget(Button(text="Sélectionner un dossier", on_press=self.show_folder_dialog))
        select_dir.add_widget(Button(text="Trier le dossier", on_press=lambda instance: run_program(self.selected_folder, "%y-%m-%d")))

        # show selected dir
        self.dir_display = BoxLayout(orientation='horizontal')
        self.dir_label = Label(text=self.selected_folder)
        self.dir_display.add_widget(self.dir_label)

        # Box principal
        box = BoxLayout(orientation='vertical')
        box.add_widget(select_dir)
        box.add_widget(self.dir_display)

        return box



    def show_folder_dialog(self, instance):
        # Make Tkinter window for the dir select
        root = tk.Tk()
        root.withdraw()  # Hide main Tkinter window
        folder_path = filedialog.askdirectory(title="Sélectionner un dossier")
        root.destroy()

        self.selected_folder = os.path.normpath(folder_path)
        self.dir_label.text = self.selected_folder



if __name__ == '__main__':
    Config.set('graphics', 'width', '550')
    Config.set('graphics', 'height', '200')

    f1 = FolderSelectorApp()
    f1.run()
    f1 = FolderSelectorApp()
    print(os.path.normpath(f1.selected_folder))
