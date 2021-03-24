import os
import re
import shutil , sys, zipfile,glob

def unzip(zip_location,clips_path):
    with zipfile.ZipFile(zip_location, 'r') as zip_ref:
        zip_ref.extractall(clips_path)

def move_to_root_folder(root_path, cur_path):
    for filename in os.listdir(cur_path):
        if os.path.isfile(os.path.join(cur_path, filename)):
            shutil.move(os.path.join(cur_path, filename), os.path.join(root_path, filename))
        elif os.path.isdir(os.path.join(cur_path, filename)):
            move_to_root_folder(root_path, os.path.join(cur_path, filename))
        else:
            sys.exit("Should never reach here.")
    if cur_path != root_path:
        os.rmdir(cur_path)

def sort_list(list):

    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    list.sort(key=alphanum_key)

    return list
def delete_small_clips(param):
        deleted_clips = []
        for root, _, files in os.walk(param):
            for f in files:
                fullpath = os.path.join(root, f)
                try:
                    if os.path.getsize(fullpath) < 100 * 1024:  # set file size in kb
                        deleted_clips.append(f)
                        os.remove(fullpath)
                except:
                    pass
        return sort_list(deleted_clips)


def delete_all_clips(param):
    for root, _, files in os.walk(param):
        for f in files:
            fullpath = os.path.join(root, f)
            try:

                os.remove(fullpath)
            except:
                pass



def merge(clips_path,video_location,call_back):
    clips_list = []
    for filename in os.listdir(clips_path):
        clips_list.append(filename)
    files = sort_list(clips_list)
    video = open(video_location, 'wb')
    count = 1
    for file in files:
        if os.path.splitext(file)[1] == '.exo':
            clip = open(os.path.join(clips_path, file), "rb")
            shutil.copyfileobj(clip, video)
            clip.close()

            call_back(count,file,len(files))
            count += 1

    video.close()


