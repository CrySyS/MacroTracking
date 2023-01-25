import os
import sys
import logging
import shutil
import configparser

from typing import  List


class Utils:
    """
    Utility functions for the project, such as config reading and logging.
    """

    logger = None
    config = configparser.ConfigParser()
    is_config_loaded: bool = False

    @classmethod
    def get_logger(cls):
        if not cls.is_config_loaded:
            raise Exception("Error: Config not loaded. Logger initialization failed!")

        if not cls.logger: 
            # create logger with 'can_compressor_logger'
            cls.logger = logging.getLogger()
            cls.logger.setLevel(logging.DEBUG)

            # create file handler which logs even debug messages and separately info messages
            fh_debug = logging.FileHandler(cls.config['Log']['folder'] + cls.config['Log']['debuglogfilename'], mode='w')
            fh_debug.setLevel(logging.DEBUG)
            
            fh_info = logging.FileHandler(cls.config['Log']['folder'] + cls.config['Log']['filename'], mode='w')
            fh_info.setLevel(logging.INFO)

            # create console handler with a higher log level
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(logging.INFO)

            # create formatter and add it to the handlers
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            fh_debug.setFormatter(formatter)
            fh_info.setFormatter(formatter)
            ch.setFormatter(formatter)

            # add the handlers to the logger
            cls.logger.addHandler(fh_debug)
            cls.logger.addHandler(fh_info)
            cls.logger.addHandler(ch)

            logging.getLogger('matplotlib.font_manager').disabled = True
            
        return cls.logger

    @classmethod
    def get_config(cls) -> List:
        if not cls.is_config_loaded:
            cls.config.read('../config/config.ini')
            cls.is_config_loaded = True
        return cls.config

    @classmethod
    def create_folder(cls, folder):
        if not os.path.isdir(folder):
            os.mkdir(folder)

    @classmethod
    def clear_out_folder(cls, folder):
        if os.path.isdir(folder):
            for the_file in os.listdir(folder):
                file_path = os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as exception:
                    print(exception)
        else:
            try:
                Utils.get_logger().warn("Folder not found. Could not be deleted.")
            except Exception as exception:
                print("Logger failed. Here is your message:")
                print(exception)

