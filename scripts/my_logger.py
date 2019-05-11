#!/usr/bin/env python3

import logging
import os

def get_console_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_console_handler())
    return logger

def get_console_and_file_logger(filename):
    # May want to add loggername parameter
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_console_handler())
    filename, verbose_filename = gen_logfile_name(filename)
    logger.addHandler(get_file_handler(filename, logging.INFO))
    logger.addHandler(get_file_handler(verbose_filename, logging.DEBUG))
    return logger

def gen_logfile_name(filename):
    f = lambda f: ".".join([f, "verbose", "log"])
    return filename, f(filename[:-4] if filename.endswith(".log") else filename)

def get_formatter():
    # create formatter
    formatter = logging.Formatter(
            "%(asctime)s [%(levelname)-8s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S")
    return formatter

def get_console_handler():
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(get_formatter())
    return console_handler

# eg. logging.INFO
def get_file_handler(filename, log_level):
    file_h = logging.FileHandler(filename)
    file_h.setLevel(log_level)
    file_h.setFormatter(get_formatter())
    return file_h

