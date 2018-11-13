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
    logger.addHandler(get_file_handler(filename))
    return logger


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

def get_file_handler(filename):
    file_h = logging.FileHandler(filename)
    file_h.setLevel(logging.DEBUG)
    file_h.setFormatter(get_formatter())
    return file_h

