from exiftool import ExifToolHelper
import os
import shutil
from datetime import datetime
import math
import threading
import time

from exiftool.exceptions import ExifToolExecuteError


class NotStrException(Exception):
    pass


class IncompleteDateFormatException(Exception):
    pass


class NoFileToProcessException(Exception):
    pass


class GreaterDivisorException(Exception):
    pass


class OrderFiles:
    """Class that extract metadata and can order files by date

    Author : Bongartz Maxime
    Date : December 2023
    This class allows files manipulations
    """

    def __init__(self, dir_path, date_format):
        """Construct all needs for the program.

        PRE : be carefull not to select files from system, applications, games etc.
        POST :  self.__dir_path is the path of the dir
                self.__treads_number is the optimal number of threads that will be used
                self.__date_format is the date format
                self.__files_meta is an empty dict
        RAISES : TypeError if date format is not a string
                 IncompleteDateFormatException if the date format doesn't include day, month and year
                 NoFileToProcessException if the program is unable to find files to process
        """

        if not (isinstance(date_format, str)):
            raise TypeError("Date format must be a string")

        if not ("%d" in date_format):
            raise IncompleteDateFormatException("No day in date format")

        if not ("%m" in date_format or "%b" in date_format):
            raise IncompleteDateFormatException("No month in date format")

        if not ("%y" in date_format or "%Y" in date_format):
            raise IncompleteDateFormatException("No year in date format")

        # Path
        self.__dir_path = os.path.normpath(dir_path)

        dir_files = []
        for file in os.listdir(self.__dir_path):
            if os.path.isfile(os.path.join(self.__dir_path, file)):
                dir_files.append(file)

        if len(dir_files) < 1:
            raise NoFileToProcessException("Nothing was detected to be processed in the selected dir")

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
            if formated_date not in os.listdir(self.__dir_path):
                os.mkdir(os.path.join(self.__dir_path, formated_date))

            # Move photos
            self.__os_move_files(self.__files_meta[date], formated_date)

        end_time = time.time()
        print("Done")
        print(f"{round((end_time - start_time), 2)}s")

    def __create_valid_list(self):
        """ Do all neceseries to fill self.__files_meta, values are day date and keys are files paths.

        PRE : self.__fill_meta_dict must build the self.__files_meta
              self.__threads_list must execute the function
        POST : returns final_list a list with full paths of all the files from self.__dir_path
        """

        # Creates files list
        files_list = os.listdir(self.__dir_path)

        # Keep only file
        final_list = []
        for file in files_list:
            if os.path.isfile(os.path.join(self.__dir_path, file)):
                final_list.append(file)

        # Full path files
        for i, file in enumerate(final_list):
            final_list[i] = os.path.join(self.__dir_path, file)

        return final_list

    def __threads_list(self, function, initial_list):
        """ Uses threads with wanted function and his list.

        PRE : no specific precondition
        POST : execute first argument function with second argument as argument, using threads
        RAISES : TypeError if function argument is not callable
                 TypeError if initial_list is not a list
        """

        if not callable(function):
            raise TypeError("First argument must be callable")

        if not isinstance(initial_list, list):
            raise TypeError("Second argument must be a list")

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

        PRE : no specific precondition
        POST : returns chunck_list a list of chunck_number lists
        RAISES : TypeError if input_list is not a list or if chunck_number is not int or float
                 GreaterDivisorException if input_list < chunck_number
        """

        if not isinstance(input_list, list):
            raise TypeError("First argument must be a list")

        if not isinstance(chunck_number, (float, int)):
            raise TypeError("Second argument must be a number")

        if len(input_list) < chunck_number:
            raise GreaterDivisorException("List can only be splited by a more litle number than his lenght")

        chunck_list = []
        step = math.floor(len(input_list) / chunck_number)
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
        """ Use exifTool to extract files metadata (even from raw photos) and builds the self.__files_meta. If exiftool
        is unable to extract metadata, the basic os file creation date is used.

        PRE : no specific precondition
        POST : self.__files_meta is a dict() where keys are dates and values are the file path
        RAISES : FileNotFoundError if a path is not a file
        """

        # Analyse potential metadatas
        print("Analysing")
        with ExifToolHelper() as et:

            metadata_elem = []
            for file_path in file_list:
                if not os.path.isfile(file_path):
                    raise FileNotFoundError("File list must contains valids files paths")

                try:
                    metadata = et.get_tags(file_path, tags=["DateTimeOriginal"])
                    metadata_elem.extend(metadata)

                except ExifToolExecuteError:

                    # Analyse os file creation date
                    result = os.path.getctime(file_path)
                    result = datetime.fromtimestamp(result)
                    day = result.strftime("%y-%m-%d")

                    if day not in self.__files_meta:
                        self.__files_meta[day] = []

                    self.__files_meta[day].append(file_path)

            for metadata_file in metadata_elem:
                day = datetime.strptime(metadata_file["EXIF:DateTimeOriginal"], "%Y:%m:%d %H:%M:%S")
                day = day.strftime("%y-%m-%d")

                if day not in self.__files_meta:
                    self.__files_meta[day] = []

                self.__files_meta[day].append(metadata_file["SourceFile"])
        print("OK")

    def __os_move_files(self, input_list, date):
        """ Os modifications: move files of <input_list> in <date> named dirs.

        PRE : no specific precondition
        POST : files are moved in corrects dirs
        RAISES : TypeError if input_list is not a list or if date is not a string
                 FileNotFoundError if elements of input_list are not files
        """

        if not isinstance(input_list, list):
            raise TypeError("First argument is not a list")

        if not isinstance(date, str):
            raise TypeError("Second argument is not a string")

        for file in input_list:
            if not os.path.isfile(file):
                raise FileNotFoundError(f"File not found: {file}")

            # Move file in dir
            destination_path = os.path.join(self.__dir_path, date)
            source_file_path = os.path.normpath(file)
            shutil.move(source_file_path, destination_path)
