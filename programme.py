class OrderFiles:
    """Class that extract metadata and can order files by date

    Author : Bongartz Maxime
    Date : December 2023
    This class analyse metadata and order files using metadata
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

        pass


    def __append_files_by_date(self, file_list):
        """ Use exifTool to extract photos metadata (even from raw photos).

        PRE : file_list must be a list of complete files paths ex: ['C:\\path\\IMG_0172.CR3', 'C:\\path\\IMG_0173.CR3']
        POST : self.__files_meta is a dict() where keys are a date and values are the files with this date name
        """

        pass


    def __use_threads(self, function, arg):
        """ Uses threads with wanted functions.

        PRE :   function must be a valid function
                arg must be the arg of the function
                arg should be a list with same length as the self.__treads_number
        POST :  use self.__treads_number number of cpu cores to process wanted function faster
        """

        pass


    def __split_list(self, input_list, chunck_number):
        """ Split list into n lists.

        PRE : input_list must be a list
              input_list must be > chunck_number
        POST : returns chunck_list a list of chunck_number lists
        """

        pass


    def __filter_list(self, input_list, by):
        """ Filter files list to 'dir' or 'file'.

        PRE : input_list must be a list of files names
              by must only be 'dir' or 'file'
        POST : returns file_list a list of file names filtered by the file or dir depending on the by param
        """

        pass


    def __os_files_sort(self, metadata_list):
        """ Os modifications.

        PRE : metadata_list is a dict, keys are strings / values is a list of dicts with filenames
        POST : order the dir chosen at the beginning by creating dirs, their names are dates, then move the files in
        correct dirs

        """

        pass
