import os
from kivy import platform
from kivy.clock import mainthread
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang.builder import Builder
from helper import move_to_root_folder, delete_small_clips, merge, unzip, delete_all_clips
from kivy.logger import Logger,LOG_LEVELS
from threading import  Thread
from kivymd.uix.filemanager import MDFileManager
if platform == 'android':
    from android.permissions import request_permission, Permission, check_permission
    from android.storage import app_storage_path
    from android.storage import primary_external_storage_path
    from android.storage import secondary_external_storage_path

    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    String = autoclass('java.lang.String')
    Uri = autoclass('android.net.Uri')
else:
    pass
    Window.size = (400,600)

class ZipvyApp(MDApp):
    action_button_data = {
        'language-python': 'Green',
        'language-php': 'Orange',
        'language-cpp': 'Blue',
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.zipsFormats = [".zip",".7z"]
        self.file_manager = MDFileManager(exit_manager=self.exit_manager,select_path=self.select_path)
        self.file_manager.ext = self.zipsFormats
    def on_start(self):
        self.icon = 'icon.ico'
        Logger.setLevel(LOG_LEVELS["debug"])
        self.zip_path = None


    def build(self):
        if platform == 'android':
            from android import loadingscreen
            loadingscreen.hide_loading_screen()
        self.theme_cls.primary_palette = "Pink"
        self.theme_cls.secondary_palette = "Dark"
        ui = Builder.load_file('main_screen.kv')
        Logger.debug("Logger is started")
        return ui

    def select_zip(self,*args):
        if platform == 'android':


            if  check_permission(Permission.WRITE_EXTERNAL_STORAGE) == False: # check permission takes str not a list
                request_permission(Permission.WRITE_EXTERNAL_STORAGE)
                request_permission(Permission.READ_EXTERNAL_STORAGE)
                request_permission(Permission.MANAGE_EXTERNAL_STORAGE)
                request_permission(Permission.MANAGE_DOCUMENTS)


                #request_permisssion takes str and request_permissions takes list
                return
            self.secondary_ext_storage = secondary_external_storage_path()
            self.primary_ext_storage = primary_external_storage_path()
            self.app_path = app_storage_path()

            Logger.debug(" Storages are \n"+ str(self.app_path ) + "\n"+str(self.primary_ext_storage))
        else:
            pass
        self.file_manager_open()





    def _select_zip(self):
        try:
            if not os.path.isfile(self.zip_path) or not os.path.splitext(self.zip_path)[1]  in self.zipsFormats:
                self._update_status( "Wrong File is Selected ")
                return
            Logger.debug(self.zip_path)
            self.zip_name = os.path.basename(self.zip_path)[:-4]
            self._update_status(str(self.zip_name) + " is selected")
            self._update_progress_bar(20)
        except Exception as e:
            Logger.exception(e)
            self._update_status("Something went wrong ... Try again")

    def file_manager_open(self):

        if platform == "android":
            self.file_manager.show("/storage/emulated/0/")
        else:
            self.file_manager.show("/")  # output manager to the screen
        self.manager_open = True

    def select_path(self, path):
        '''It will be called when you click on the file name
        or the catalog selection button.

        :type path: str;
        :param path: path to the selected directory or file;
        '''
        self.zip_path = path
        print("printing selected zip path ... "+str(path))
        self.exit_manager()

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''

        self.manager_open = False
        self.file_manager.close()
        if self.zip_path == None:
            self._update_status("No file is selected")
            return
        select_zip_thread = Thread(target=self._select_zip)
        select_zip_thread.start()

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True



    def convert(self,*args):

        if platform == 'android':
            if  check_permission(Permission.WRITE_EXTERNAL_STORAGE) == False: # check permission takes str not a list
                request_permission(Permission.WRITE_EXTERNAL_STORAGE)
                request_permission(Permission.READ_EXTERNAL_STORAGE)# request_permisssion takes str and request_permissions takes list
                return
            # Make a Folder for Zip
            # Make ChandanVideo Folder in Internal Storage
            if self.zip_path == None or os.path.splitext(self.zip_path)[1] != '.zip':
                self.root.ids.status_label.text = "Select a zip first "
                return
            self._update_status("Please Wait ... Checking Zip")
            self.clips_path = os.path.join(self.app_path, self.zip_name)
            self.video_folder = os.path.join(self.primary_ext_storage, "Zipvy")
            self.video_location = os.path.join(self.video_folder, self.zip_name+".mp4")
            Logger.debug("Clips Path : "+str(self.clips_path)  +
                        "\n video_folder : "+str(self.video_folder)+
                        "\n video_path:" + str(self.video_location) )

            convert_thread = Thread(target=self._convert)
            convert_thread.start()



        else:
            self.root.ids.prog.value = 75
            self.root.ids.status_label.text = " I am running in "+str(platform)
            print(" I am running in "+str(platform))

    def _convert(self):
        try:
            if not os.path.exists(self.clips_path):
                os.makedirs(self.clips_path)
            if not os.path.exists(self.video_folder):
                os.makedirs(self.video_folder)

            # Extract Zip to the folder
            unzip(self.zip_path, self.clips_path)
            self._update_status("Unzipped")
            Logger.debug("Unzipped clips for file " + str(self.zip_path))
            Logger.debug("clips are available at  " + str(self.clips_path))

            # move clips to root
            move_to_root_folder(self.clips_path, self.clips_path)
            Logger.debug("Moving clips to root dir is done")
            # Delete Small clips ...

            deleted_clips = delete_small_clips(self.clips_path)
            Logger.debug("Following Clips are deleted due to low size (less than 100kb)")

            for deleted_clip in deleted_clips:
                Logger.debug(deleted_clip)

            self._update_progress_bar(50)
            self._update_status("Ready to make video")
            # merge clips and make video

            Logger.debug("Entered to merging try block")
            merge(self.clips_path, self.video_location, self._update_progress)
            Logger.debug("End of merging try block")

            # Clearing Temp dir
            delete_all_clips(self.clips_path)
            self._update_status(os.path.basename(self.video_location)[:-4]+" is now ready to watch")
            self._toast("Always use Mx/Vlc Player to watch Videos")

        except Exception:
            Logger.exception('Something happened wrong at merge')
            self._update_status("Something happened wrong at merge")




    def open_video_folder(self,*args):
        if platform == 'android':
            pass
        pass
    def open_video(self,*args):
        if platform == 'android':
            pass
            #self._open(self.video_location)

    def action_button_callback(self,instance):
        if instance.icon == 'language-python':
            self.theme_cls.primary_palette = "Green"
        if instance.icon == 'language-php':
            self.theme_cls.primary_palette = "Orange"
        if instance.icon == 'language-cpp':
            self.theme_cls.primary_palette = "Blue"



    def _update_progress(self,file_no,file_name,files):
        percentage = int(file_no*100/files)

        self._update_progress_bar(50+int(percentage/2))

        progress_text  = "Merging Clips " + str(file_no) +"/"+str(files)+" "+ str(percentage)+" %"

        self._update_status(progress_text)

        Logger.debug(progress_text+" of "+ str(file_name))

    @mainthread
    def _update_status(self,text):
        self.root.ids.status_label.text = str(text)

    @mainthread
    def _update_progress_bar(self,value):
        self.root.ids.prog.value = int(value)

    def _open(self, video_location):
        try:
            from kivy.setupconfig import USE_SDL2
            if platform == 'android':
                from jnius import cast
                from jnius import autoclass
                if USE_SDL2:
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                else:
                    PythonActivity = autoclass('org.renpy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                String = autoclass('java.lang.String')
                Uri = autoclass('android.net.Uri')
                File = autoclass('java.io.File')

                shareIntent = Intent(Intent.ACTION_SEND)
                shareIntent.setType('"video/*"')
                VideoFile = File(video_location)
                uri = Uri.fromFile(VideoFile)
                parcelable = cast('android.os.Parcelable', uri)
                shareIntent.putExtra(Intent.EXTRA_STREAM, parcelable)
                currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
                currentActivity.startActivity(shareIntent)
        except Exception as e:
            Logger.exception("Unable to share video")

    def _toast(self,text):
        try:
            from jnius import autoclass, cast
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            context = PythonActivity.mActivity
            AndroidString = autoclass('java.lang.String')
            Toast = autoclass('android.widget.Toast')
            duration = Toast.LENGTH_SHORT
            text_char_sequence = cast('java.lang.CharSequence', AndroidString(text))
            toast = Toast.makeText(context, text_char_sequence, duration)
            toast.show()
        except Exception as e:
             Logger.exception(e)


if __name__ == '__main__':

    ZipvyApp().run()