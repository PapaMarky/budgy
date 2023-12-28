import os.path
from pathlib import Path

import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIPanel, UIButton
from pygame_gui.windows.ui_message_window import UIMessageWindow
from pygame_gui.windows.ui_confirmation_dialog import UIConfirmationDialog

import budgy.gui
from budgy.gui.constants import MARGIN, BUTTON_HEIGHT, BUTTON_WIDTH
from budgy.gui.dialogs import show_confirmation_dialog, show_file_dialog, is_confirmation_dialog, is_file_dialog
import budgy.gui.events
from budgy.gui.function_subpanel import BudgyFunctionSubPanel
from budgy.gui.record_view_panel import RecordViewPanel


CONFIRM_IMPORT_TITLE = 'Confirm Import'
CONFIRM_DELETE_ALL_TITLE = 'Confirm Delete All Data'
IMPORT_FILE_DIALOG_TITLE = 'Import Data File'

def is_confirm_delete_all_dialog(element):
    return is_confirmation_dialog(element, CONFIRM_DELETE_ALL_TITLE)

def show_confirm_delete_all_dialog():
    show_confirmation_dialog(CONFIRM_DELETE_ALL_TITLE,
                             'Selecting OK will DELETE ALL RECORDS from the database')
def is_confirm_import_dialog(element):
    return is_confirmation_dialog(element, CONFIRM_IMPORT_TITLE)

def show_confirm_import_dialog():
    long_desc = 'Selecting OK will import the data from the file into the database'
    show_confirmation_dialog(CONFIRM_IMPORT_TITLE, long_desc)
def is_import_file_dialog(element):
    return is_file_dialog(element, IMPORT_FILE_DIALOG_TITLE)
def show_import_data_file_dialog(initial_path):
    show_file_dialog(IMPORT_FILE_DIALOG_TITLE,
                     initial_path,
                     allowed_suffixes=['.ofx', '.qfx'])


class BudgyDataPanel(BudgyFunctionSubPanel):
    def __init__(self, config_in, function_panel, *args, **kwargs):
        super().__init__(config_in, function_panel, *args, **kwargs)
        self._import_data_button = UIButton(
            pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT),
            'Import Data',
            self.ui_manager,
            container=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'left'
            }
        )
        x = self._import_data_button.get_relative_rect().right
        y = self._import_data_button.get_relative_rect().top
        w = BUTTON_WIDTH
        h = self._import_data_button.get_relative_rect().height
        self._clear_data_button = UIButton(
            pygame.Rect(x, y, w, h),
            'Clear Data',
            self.ui_manager,
            container=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'left'
            }
        )

        x = 0
        y = self._clear_data_button.get_relative_rect().bottom + MARGIN

        w, h = self.get_relative_rect().size
        w -= 6 * MARGIN
        h -= 6 * MARGIN + y
        rr = pygame.Rect(x, y, w, h)
        # rr.bottomright = (-MARGIN, -MARGIN)
        self._records_view_panel = RecordViewPanel(
            rr,
            manager=self.ui_manager,
            container=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'bottom', 'right': 'right'
            },
            object_id=ObjectID(object_id='#records_view_panel')
        )

        # TODO do we need these?
        self.import_path = None

    def set_data(self, new_data):
        self._records_view_panel.set_data(new_data)

    def process_confirm_dialog_events(self, event: pygame.event.Event) -> bool:
        if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if is_confirm_import_dialog(event.ui_element):
                print(f'Importing data from {self.import_path}')
                event_data = {
                    'path': self.import_path
                }
                self.budgy_config.import_data_path = self.import_path
                pygame.event.post(pygame.event.Event(budgy.gui.events.DATA_SOURCE_CONFIRMED, event_data))
                self.import_path = None
                return True
            if is_confirm_delete_all_dialog(event.ui_element):
                print(f'Deleting all data from database')
                event_data = {}
                pygame.event.post(pygame.event.Event(budgy.gui.events.DELETE_ALL_DATA_CONFIRMED, event_data))
                return True

    def process_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._import_data_button:
                print('IMPORT DATA')
                # Create the import data file dialog
                rect = pygame.Rect(0, 0, 500, 400)
                show_import_data_file_dialog(self.budgy_config.import_data_path)
                self._import_data_button.disable()
                return True
            if event.ui_element == self._clear_data_button:
                event_data = {
                    'ui_element': self
                }
                pygame.event.post(pygame.event.Event(budgy.gui.events.DELETE_ALL_DATA, event_data))
                return True
        if event.type == pygame_gui.UI_WINDOW_CLOSE and is_import_file_dialog(event.ui_element):
            self._import_data_button.enable()
            return True
        if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED and is_import_file_dialog(event.ui_element):
            print(f' - PATH PICKED: {event.text}')
            event_data = {
                'import_path': event.text,
                'ui_element': self
            }
            pygame.event.post(pygame.event.Event(budgy.gui.events.DATA_SOURCE_SELECTED, event_data))
            return True
        if event.type == budgy.gui.events.DATA_SOURCE_SELECTED:
            self.import_path = event.import_path
            print(f'LOAD DATA: {self.import_path}')
            if not os.path.exists(self.import_path):
                rect = pygame.Rect(100, 100, 400, 200)
                UIMessageWindow(rect,
                                f'<br/><b>File does not exist:</b> <br/>{os.path.basename(event.import_path)}',
                                manager=None,
                                window_title='File Missing')
                self.import_path = None
            else:
                # import the data
                show_confirm_import_dialog()
            return True
        if event.type == budgy.gui.events.DELETE_ALL_DATA:
            print('CLEAR DATA (data panel)')
            show_confirm_delete_all_dialog()
            return True
        if self.process_confirm_dialog_events(event):
            return True

        return False