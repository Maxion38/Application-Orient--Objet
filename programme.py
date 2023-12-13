from exiftool import ExifToolHelper
import os
import subprocess
from datetime import datetime
import math
import threading
import time


def run_program(path, dir_name):
    start_time = time.time()

    files_path = path + "\\"
    files_list = os.listdir(files_path)
    NUMBER_OF_TREADS = math.floor(os.cpu_count() / 1.14)  # optimal threads number (theory)
    metadata = []


    ''' Filter files list to 'dir' or 'file' '''
    def filter_list(input_list, filter):
        if filter == 'dir':
            dir_list = []
            for file in input_list:
                if os.path.isdir(files_path + file):
                    dir_list.append(file)

            return dir_list

        if filter == 'file':
            file_list = []
            for file in input_list:
                if os.path.isfile(files_path + file):
                    file_list.append(file)

            return file_list


    ''' Split list into n lists '''
    def split_list(input_list, chunck_number):
        if chunck_number > len(input_list):
            print("annomalie: trop de threads")


        chunck_list = []
        step = math.floor(len(input_list)/chunck_number)
        start = 0
        stop = 0
        for i in range(chunck_number):
            temp_list = []
            stop += step
            for pos in range(start, stop):
                temp_list.append(input_list[pos])

            chunck_list.append(temp_list)
            start += step

        # Rest
        rest = stop
        i = 0
        for pos in range(rest, len(input_list)):
            chunck_list[i].append(input_list[pos])
            i += 1
        return chunck_list


    # Create files path
    files_path_list = filter_list(files_list, 'file')
    print(files_list)
    for i, file in enumerate(files_path_list):
        files_path_list[i] = files_path + file

    # Prepare multi threading
    splited_files_list = split_list(files_path_list, NUMBER_OF_TREADS)


    def get_metadata(file_list):
        print("Analysing")
        with ExifToolHelper() as et:
            metadata_elem = et.get_tags(file_list, tags=["DateTimeOriginal"])
            metadata.append(metadata_elem)
        print("OK")


    ''' Os modifications '''
    def os_files_sort(metadata_list):
        for i, file in enumerate(metadata_list):
            source_file_path = file["SourceFile"]
            file_date_taken = file["EXIF:DateTimeOriginal"]
            # Format date name
            file_date_taken = datetime.strptime(file_date_taken, "%Y:%m:%d %H:%M:%S")
            file_date_taken = file_date_taken.strftime(dir_name)

            # Move file in dir
            destination_path = files_path + file_date_taken
            source_file_path = os.path.normpath(source_file_path)
            subprocess.run('move "' + source_file_path + '" "' + destination_path + '"', shell=True)


    ''' Uses threads with wanted functions '''
    def use_threads(function, func_arg):
        # Open threads
        threads = []
        for i in range(NUMBER_OF_TREADS):
            thread = threading.Thread(target=function, args=(func_arg[i],))
            threads.append(thread)
            thread.start()

        # Wait threads
        for thread in threads:
            thread.join()


    # Get metadata
    use_threads(get_metadata, splited_files_list)
    all_files_metadata = []
    for metadata_list in metadata:
        for file in metadata_list:
            all_files_metadata.append(file)
    print("L'analyse des fichiers est terminée")


    future_dir_set = set()
    # Create dirs
    for file in all_files_metadata:
        file_date_taken = file["EXIF:DateTimeOriginal"]
        # Format date name
        file_date_taken = datetime.strptime(file_date_taken, "%Y:%m:%d %H:%M:%S")
        file_date_taken = file_date_taken.strftime(dir_name)
        future_dir_set.add(file_date_taken)

    dir_list = filter_list(files_list, 'dir')
    for dir in future_dir_set:
        if dir not in dir_list:
            os.mkdir(files_path + dir)
            print("Dir " + dir + " created")

    # Move photos
    use_threads(os_files_sort, metadata)
    print("Finished")

    end_time = time.time()
    print(str(round(end_time - start_time, 2)) + "s")
