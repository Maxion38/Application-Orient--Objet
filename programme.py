from exiftool import ExifToolHelper
import os
import shutil
from datetime import datetime
import math
import threading
import time


class OrderFiles:
    """Class that extract metadata and can order files by date

    Author : Bongartz Maxime
    Date : December 2023
    This class allows files manipulations
    """

    def __init__(self, dir_path, date_format):
        """Construct all needs for the program.

        PRE : dir_path should be a valid dir path
              date_format must be usable by strftime function
        POST :  self.__dir_path is the path of the dir
                self.__treads_number is the optimal number of threads that will be used
                self.__date_format is the date format
                self.__files_meta is an empty dict
        """

        # Path
        self.__dir_path = dir_path

        # Utils
        self.__treads_number = math.floor(os.cpu_count() / 1.14)  # optimal threads number (theory)
        self.__date_format = date_format

        # Main dict
        self.__files_meta = {}


    def os_order_files(self):
        """Order all the files in dirs. A dir is named by de day date of a file.

        PRE : self.__build_meta_dict() must build the self.__files_meta dict
              self.__os_move_files() must move all the files according to the self.__files_meta dict
        POST : builds self.__files_meta dict
               make dirs and move photos in
        """

        start_time = time.time()

        # Create list
        valid_list = self.__create_valid_list()

        # Builds __files_meta
        self.__threads_list(self.__fill_meta_dict, valid_list)

        for date in self.__files_meta:
            # Format date name
            formated_date = datetime.strptime(date, "%y-%m-%d")
            formated_date = formated_date.strftime(self.__date_format)

            # Create dir
            os.mkdir(self.__dir_path + formated_date)

            # Move photos
            self.__os_move_files(self.__files_meta[date], formated_date)

        end_time = time.time()
        print("Done")
        print(str(round((end_time - start_time), 2)) + "s")


    def __create_valid_list(self):
        """ Do all neceseries to fill self.__files_meta, values are day date and keys are files paths.

        PRE : self.__fill_meta_dict must build the self.__files_meta
              self.__threads_list must thread the function
        POST : returns final_list a list with full paths of all the files from self.__dir_path
        """

        # Creates files list
        files_list = os.listdir(self.__dir_path)

        # Keep only file
        final_list = []
        for file in files_list:
            if os.path.isfile(self.__dir_path + file):
                final_list.append(file)

        # Files to full path files
        for i, file in enumerate(final_list):
            final_list[i] = self.__dir_path + file

        return final_list


    def __threads_list(self, function, initial_list):
        """ Uses threads with wanted functions and their list.

        PRE :   function must be a function
                initial_list must be the argument of the function
                initial_list must be a list
        POST :  use self.__treads_number number of cpu cores to process wanted function faster
        """

        # Split list by number of threads
        splited_files_list = initial_list

        if self.__treads_number < len(initial_list):
            splited_files_list = self.__split_list(initial_list, self.__treads_number)

            # Open threads
            threads = []
            for tn in range(self.__treads_number):
                thread = threading.Thread(target=function, args=(splited_files_list[tn],))
                threads.append(thread)
                thread.start()

            # Wait threads
            for thread in threads:
                thread.join()

        else:
            function(splited_files_list)


    def __split_list(self, input_list, chunck_number):
        """ Split list into n lists.

        PRE : input_list must be a list
              input_list must be > chunck_number
        POST : returns chunck_list a list of chunck_number lists
        """

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


    def __fill_meta_dict(self, file_list):
        """ Use exifTool to extract files metadata (even from raw photos) and builds the self.__files_meta.

        PRE : file_list must be a list of complete files paths ex: ['C:\\path\\IMG_0172.CR3', 'C:\\path\\IMG_0173.CR3']
              file_list must refer to files that are compatible with ExifTool
        POST : self.__files_meta is a dict() where keys are dates and values are the file path
        """

        print("Analysing")
        with ExifToolHelper() as et:
            metadata_elem = et.get_tags(file_list, tags=["DateTimeOriginal"])

            for metadata_file in metadata_elem:
                day = datetime.strptime(metadata_file["EXIF:DateTimeOriginal"], "%Y:%m:%d %H:%M:%S")
                day = day.strftime("%y-%m-%d")

                if day not in self.__files_meta:
                    self.__files_meta[day] = []

                self.__files_meta[day].append(metadata_file["SourceFile"])

        print("OK")


    def __os_move_files(self, metadata_list, date):
        """ Os modifications: move files in correct dirs.

        PRE : metadata_list is a dict where keys are strings and values is a list of files paths
        POST : files are moved in corrects dirs
        """

        for fn, meta_file in enumerate(metadata_list):

            # Move file in dir
            destination_path = self.__dir_path + date
            source_file_path = os.path.normpath(meta_file)
            shutil.move(source_file_path, destination_path)
