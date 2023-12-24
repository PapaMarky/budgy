import os.path
from pathlib import Path

import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIPanel, UIButton
from pygame_gui.windows.ui_message_window import UIMessageWindow
from pygame_gui.windows.ui_confirmation_dialog import UIConfirmationDialog

import budgy.gui
import budgy.gui.events
from budgy.gui.function_subpanel import BudgyFunctionSubPanel
from budgy.gui.import_data_dialog import ImportDataDialog
from budgy.gui.dialogs import is_import_file_dialog, show_import_data_file_dialog

class BudgyDataPanel(BudgyFunctionSubPanel):
    def __init__(self, config_in, function_panel, *args, **kwargs):
        super().__init__(config_in, function_panel, *args, **kwargs)
        self._import_data_button = UIButton(
            pygame.Rect(0, 0, budgy.gui.BUTTON_WIDTH, budgy.gui.BUTTON_HEIGHT),
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
        w = budgy.gui.BUTTON_WIDTH
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
        y = self._clear_data_button.get_relative_rect().bottom + budgy.gui.MARGIN

        w, h = self.get_relative_rect().size
        w -= 6 * budgy.gui.MARGIN
        h -= 6 * budgy.gui.MARGIN + y
        rr = pygame.Rect(x, y, w, h)
        # rr.bottomright = (-budgy.gui.MARGIN, -budgy.gui.MARGIN)
        self._records_view_panel = UIPanel(
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
        self.confirm_import = None
        self.config_delete_all = None

    def process_confirm_dialog_events(self, event: pygame.event.Event) -> bool:
        if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if event.ui_element == self.confirm_import:
                print(f'Importing data from {self.import_path}')
                event_data = {
                    'path': self.import_path
                }
                self.budgy_config.import_data_path = self.import_path
                pygame.event.post(pygame.event.Event(budgy.gui.events.DATA_SOURCE_CONFIRMED, event_data))
                self.import_path = None
                return True
            if event.ui_element == self.config_delete_all:
                print(f'Deleting all data from database')
                event_data = {}
                pygame.event.post(pygame.event.Event(budgy.gui.events.DELETE_ALL_DATA_CONFIRMED, event_data))
                return True
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.confirm_import:
                self.confirm_import = None
            if event.ui_element == self.config_delete_all:
                self.config_delete_all = None
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
                rect = pygame.Rect(100, 100, 400, 200)
                self.confirm_import = UIConfirmationDialog(
                    rect,
                    'Selecting OK will import the data from the file into the database',
                    window_title='Confirm Import'
                )
            return True
        if event.type == budgy.gui.events.DELETE_ALL_DATA:
            print('CLEAR DATA (data panel)')
            rect = pygame.Rect(100, 100, 400, 200)
            self.config_delete_all = UIConfirmationDialog(
                rect,
                'Selecting OK will DELETE ALL RECORDS from the database',
                window_title='Confirm Delete All Data'
            )
            return True
        if self.process_confirm_dialog_events(event):
            return True

        return False