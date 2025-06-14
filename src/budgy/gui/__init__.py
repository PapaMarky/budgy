import logging
import os

from budgy.gui import configdata
from budgy.gui import data_panel

install_path = os.path.dirname(__file__)
_data_dir = os.path.join(install_path, 'data')

def get_data_dir():
    return _data_dir if os.path.exists(_data_dir) else None

def get_data_file_path(file_name):
    data_dir = get_data_dir()
    if data_dir is None:
        return None
    path = os.path.join(data_dir, file_name)
    return path if os.path.exists(path) else None

_themes_dir = os.path.join(_data_dir, 'themes')

def get_themes_dir():
    logging.debug(f'        File: {__file__}')
    logging.debug(f'Install Path: {install_path}')
    logging.debug(f'    Data Dir: {_data_dir}')
    logging.debug(f'  Themes Dir: {_themes_dir}')
    return _themes_dir if os.path.exists(_themes_dir) else None

def get_themes_file_path(file_name):
    themes_dir = get_themes_dir()
    logging.debug(f'themes_dir: {themes_dir}')
    if themes_dir is None:
        return None
    path = os.path.join(themes_dir, file_name)
    return path if os.path.exists(path) else None
