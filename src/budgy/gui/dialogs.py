import pygame
from pygame_gui.windows import UIFileDialog
from pygame_gui.core import ObjectID

IMPORT_FILE_DIALOG_TITLE = 'Import Data File'
def is_import_file_dialog(element):
    return isinstance(element, UIFileDialog) and element.window_display_title == IMPORT_FILE_DIALOG_TITLE
def show_import_data_file_dialog(initial_path):
    show_file_dialog(IMPORT_FILE_DIALOG_TITLE,
                     initial_path,
                     allowed_suffixes=['.ofx', '.qfx'])

def show_file_dialog(title, initial_file_path,
                     allowed_suffixes=[],
                     rect=None, manager=None,
                     allow_existing_files_only=True,
                     allow_picking_directories=False):
    if rect is None:
        rect = pygame.Rect(0, 0, 500, 400)

    UIFileDialog(rect,
                 manager=manager,
                 window_title=title,
                 initial_file_path=initial_file_path,
                 object_id=ObjectID(object_id='#file_dialog'),
                 allow_existing_files_only=allow_existing_files_only,
                 allow_picking_directories=allow_picking_directories,
                 allowed_suffixes=allowed_suffixes,
                 visible=True)
