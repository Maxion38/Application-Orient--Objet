# Take all the files out of the forlders
import shutil
import os
import time

start_time = time.time()

files_path = "C:\\Users\\mbong\\OneDrive\\Bureau\\python_photo_sort\\"

dir_list = os.listdir(files_path)

for directory in dir_list:
    if os.path.isdir(files_path + directory):
        file_path_list = os.listdir(files_path + directory)

        for file in file_path_list:
            current_file_path = files_path + directory + "\\" + file
            destination_path = files_path + file
            shutil.move(current_file_path, destination_path)
        print(directory + " unpacked")
print("Directories emptied")

for file_dir in dir_list:
    dir_path = files_path + file_dir
    if os.path.isdir(dir_path):
        os.rmdir(files_path + file_dir)

print("Directories removed")
end_time = time.time()
print(str(round(end_time - start_time, 2)) + "s")