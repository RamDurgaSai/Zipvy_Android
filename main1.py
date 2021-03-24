import os
from kivy import platform
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang.builder import Builder
from helper import move_to_root_folder, delete, merge, unzip
from kivymd.uix.filemanager import MDFileManager

if platform == 'android':
    from android.permissions import check_permission, request_permission,Permission
    from android.storage import app_storage_path
    from android.storage import primary_external_storage_path
    from android.storage import secondary_external_storage_path
else:
    pass
    #Window.size = (400,600)

class ZipvyApp(MDApp):
    action_button_data = {
        'language-python': 'Green',
        'select-color': 'Orange',
        'language-cpp': 'Blue',
    }


    def __init__(self):
        super(ZipvyApp, self).__init__()
        self.file_manager = MDFileManager(exit_manager = self.exit_manager,select_path = self.select_path)




    def build(self):
        Window.bind(on_keyboard=self._events)
        self.theme_cls.primary_palette = "Pink"
        self.theme_cls.secondary_palette = "Dark"
        ui = Builder.load_file('main_screen1.kv')


        return ui

    def select_zip(self,*args):
        if platform == 'android':
            if not check_permission([Permission.WRITE_EXTERNAL_STORAGE]):
                request_permission([Permission.WRITE_EXTERNAL_STORAGE])
            self.secondary_ext_storage = secondary_external_storage_path()
            self.primary_ext_storage = primary_external_storage_path()
            self.app_path = app_storage_path()
            self.file_manager_open()
            if self.zip_path == None or os.path.splitext(self.zip_path)[1] != '.zip':
                self.root.ids.status_label.text = "Wrong File is Selected "
                return
            self.zip_name = os.path.basename(self.zip_path)[:-4]
            self.root.ids.status_label.text = str(self.zip_name)

        else:
            self.root.ids.prog.value = 20
            self.root.ids.status_label.text = "Wrong File is Selected "
            print(" I am running in "+str(platform))








    def convert(self,*args):

        if platform == 'android':
            # Make a Folder for Zip
            # Make ChandanVideo Folder in Internal Storage
            self.clips_path = os.path.join(self.app_path, self.zip_name)
            self.video_folder = os.path.join(self.primary_ext_storage, "Zipvy")
            self.video_location = os.path.join(self.video_folder, self.zip_name+".mp4")

            if not os.path.exists(self.clips_path):
                os.makedirs(self.clips_path)
            if not os.path.exists(self.video_folder):
                os.makedirs(self.video_folder)



            # Extract Zip to the folder
            unzip(self.zip_path,self.clips_path)
            self.root.ids.status_label.text = "Unzipped"

            # move clips to root
            move_to_root_folder(self.clips_path,self.clips_path)
            # Delete Small clips ...
            delete(self.clips_path)

            self.root.ids.prog.value = 50
            self.root.ids.status_label.text = "Ready to make video"
            # merge clips and make video

            merge(self.clips_path,self.video_location,self._update_progress)

            self.root.ids.prog.value = 100
        else:
            self.root.ids.prog.value = 75
            self.root.ids.status_label.text = " I am running in "+str(platform)
            print(" I am running in "+str(platform))




    def open_video_folder(self,*args):
        if platform == 'android':
            self._open(self.video_folder)
    def open_video(self,*args):
        if platform == 'android':
            self._open(self.video_location)

    def file_manager_open(self):
        self.file_manager.show('/')  # output manager to the screen
        self.manager_open = True






    def select_path(self, path):
        '''It will be called when you click on the file name
        or the catalog selection button.

        :type path: str;
        :param path: path to the selected directory or file;
        '''

        self.exit_manager()
        self.zip_path = path

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''

        self.manager_open = False
        self.file_manager.close()

    def _events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    def action_button_callback(self,instance):
        if instance.icon == 'language-python':
            self.theme_cls.primary_palette = "Green"
        if instance.icon == 'select-color':
            self.theme_cls.primary_palette = "Orange"
        if instance.icon == 'language-cpp':
            self.theme_cls.primary_palette = "Blue"



    def _update_progress(self,file,files):
        percentage = int(file*100/files)
        self.root.ids.prog.value = 50 + int(percentage/2)
        self.root.ids.status_label.text = "Merging Clips " + file +"/"+files+" "+ str(percentage)+" %"
if __name__ == '__main__':

    ZipvyApp().run()