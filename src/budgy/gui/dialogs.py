import pygame
from pygame_gui.core import ObjectID
from pygame_gui.windows import UIFileDialog
from pygame_gui.windows.ui_confirmation_dialog import UIConfirmationDialog

def is_confirmation_dialog(element, window_title):
    return isinstance(element, UIConfirmationDialog) and element.window_display_title == window_title

def show_confirmation_dialog(window_title, action_long_desc, rect=None):
    if rect is None:
        rect = pygame.Rect(100, 100, 400, 200)
    UIConfirmationDialog(
        rect,
        action_long_desc,
        window_title=window_title
    )

def is_file_dialog(element, window_title):
    return isinstance(element, UIFileDialog) and element.window_display_title == window_title
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
