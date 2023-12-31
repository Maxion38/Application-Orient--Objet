from exiftool import ExifToolHelper
import os
import shutil
from datetime import datetime
import math
import threading


class OrderFiles:
    """Class that extract metadata and can order files by date

    Author : Bongartz Maxime
    Date : December 2023
    This class allows files manipulations
    """

    def __init__(self, dir_path, date_format):
        """Keep the paths needed and get date metadata.

        PRE : dir_path should be a valid dir path
              date_format must be usable by strftime function
        POST :  self.__dir_path is the dir selected to be sorted
                self.__files_list is the list of files names in self.__dir_path
                self.__treads_number is the optimal number of threads that will be used
                self.files_meta is an empty dict
                self.__date_format is the date format
                self.__files_path_list is the list of files paths + names in self.__dir_path
                self.__splited_files_list is the __files_path_list splited by the number of threads

        """

        # Paths
        self.__dir_path = dir_path
        self.__files_list = os.listdir(self.__dir_path)

        # Others
        self.__treads_number = math.floor(os.cpu_count() / 1.14)  # optimal threads number (theory)
        self.files_meta = {}
        self.__date_format = date_format

        # Do all neceseries to get the dict(), values are day date and keys are files paths

        # Create files path list
        self.__files_path_list = []
        for file in self.__files_list:
            if os.path.isfile(self.__dir_path + file):
                self.__files_path_list.append(file)

        for i, file in enumerate(self.__files_path_list):
            self.__files_path_list[i] = self.__dir_path + file

        # Get metadata
        self.__use_threads_list(self.__append_files_by_date, self.__files_path_list)


        for date in self.files_meta:
            # Format date name
            formated_date = datetime.strptime(date, "%y-%m-%d")
            formated_date = formated_date.strftime(self.__date_format)

            # Create dir
            os.mkdir(self.__dir_path + formated_date)

            # Move photos
            self.__os_files_sort(self.files_meta[date])



    def __append_files_by_date(self, file_list):
        """ Use exifTool to extract photos metadata (even from raw photos).

        PRE : file_list must be a list of complete files paths ex: ['C:\\path\\IMG_0172.CR3', 'C:\\path\\IMG_0173.CR3']
        POST : self.__files_meta is a dict() where keys are a date and values are the files with this date name
        """

        print("Analysing")
        with ExifToolHelper() as et:
            metadata_elem = et.get_tags(file_list, tags=["DateTimeOriginal"])

            for metadata_file in metadata_elem:
                day = datetime.strptime(metadata_file["EXIF:DateTimeOriginal"], "%Y:%m:%d %H:%M:%S")
                day = day.strftime("%y-%m-%d")

                if day not in self.files_meta:
                    self.files_meta[day] = []

                self.files_meta[day].append(metadata_file)

        print("OK")


    def __use_threads_list(self, function, initial_list):
        """ Uses threads with wanted functions.

        PRE :   function must be a valid function
                arg must be the arg of the function
                arg should be a list with same length as the self.__treads_number
        POST :  use self.__treads_number number of cpu cores to process wanted function faster
        """

        # Split list by number of threads
        splited_files_list = self.__files_path_list

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


    def __os_files_sort(self, metadata_list):
        """ Os modifications.

        PRE : metadata_list is a dict, keys are strings / values is a list of dicts with filenames
        POST : order the dir chosen at the beginning by creating dirs, their names are dates, then move the files in
        correct dirs

        """
        for fn, meta_file in enumerate(metadata_list):
            source_file_path = meta_file["SourceFile"]
            file_date_taken = meta_file["EXIF:DateTimeOriginal"]
            # Format date name
            file_date_taken = datetime.strptime(file_date_taken, "%Y:%m:%d %H:%M:%S")
            file_date_taken = file_date_taken.strftime(self.__date_format)

            # Move file in dir
            destination_path = self.__dir_path + file_date_taken
            source_file_path = os.path.normpath(source_file_path)
            shutil.move(source_file_path, destination_path)
