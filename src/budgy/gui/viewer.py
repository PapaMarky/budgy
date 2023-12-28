import argparse
import logging
from pathlib import Path

import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.windows import UIFileDialog, UIMessageWindow
from pygame_gui_extras.app import GuiApp
from pygame_gui.elements import UIPanel, UIButton

from budgy.core.database import BudgyDatabase
from budgy.core import load_ofx_file
from budgy.version import __version__ as package_version

import budgy.gui

from budgy.gui.data_panel import BudgyDataPanel
from budgy.gui.top_panel import TopPanel
from budgy.gui.message_panel import MessagePanel
from budgy.gui.function_panel import BudgyFunctionPanel
from budgy.gui.configdata import BudgyConfig
from budgy.gui.events import SELECT_DATABASE, OPEN_DATABASE, DELETE_ALL_DATA, post_show_message, post_clear_messages
from budgy.gui.constants import BUTTON_WIDTH, BUTTON_HEIGHT, MARGIN

class BudgyViewerApp(GuiApp):

    def __init__(self, size=(1280, 960)):
        self._title = f'Budgy Data Viewer: v{package_version}'
        super().__init__(size, title=self._title)
        self._args = self._parse_args()
        themes_file = budgy.gui.get_themes_file_path('theme.json')
        print(f'themes file: {themes_file}')
        if themes_file:
            self._ui_manager.get_theme().load_theme(themes_file)
        else:
            print(f'WARNING: theme file not found')
        self._quit_button:UIButton = None
        self._button_rect:pygame.Rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
        self._database:BudgyDatabase = None
        self._config:BudgyConfig = BudgyConfig()

    @property
    def database_path(self):
        return self._config.config_dict['database']['path']

    def setup(self):
        tp_height = (3 * BUTTON_HEIGHT) + (6 * MARGIN)
        mp_height = (3 * BUTTON_HEIGHT) + (4 * MARGIN)
        rect = pygame.Rect(0, 0,
                        self.size[0], tp_height)
        self.top_panel = TopPanel(
            self._config,
            rect,
            1,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'right'
            },
            margins={'top': MARGIN, 'left': MARGIN,
                     'bottom': MARGIN, 'right': MARGIN},
            manager=self.ui_manager,
            object_id=ObjectID(class_id='#top-panel')
        )
        x = 0
        y = self.top_panel.relative_rect.bottom
        w = self.size[0]
        h = (self.size[1] - y - MARGIN) - mp_height
        function_panel_rect = pygame.Rect(x, y, w, h)
        self.function_panel = \
            BudgyFunctionPanel(self._config,
                               function_panel_rect,
                               starting_height=1,
                               manager=self.ui_manager,
                               anchors={
                                   'top': 'top', 'left': 'left',
                                   'bottom': 'bottom', 'right': 'right'
                               },
                               object_id=ObjectID(object_id='#function-panel')
            )
        rect = pygame.Rect(x, -mp_height,
                           w, mp_height)
        self.message_panel = MessagePanel(
            rect,
            starting_height=1,
            manager=self.ui_manager,
            anchors={
                'top': 'bottom', 'left': 'left',
                'bottom': 'bottom', 'right': 'right'
            },
            object_id=ObjectID(class_id='#message-panel')
        )
        # Once the UI is setup, open the database
        self.open_database()
        target_date = self._config.retirement_target_date
        self.top_panel.set_retirement_info(target_date)


    def open_database(self):
        dbpath = Path(self.database_path).expanduser()
        print(f'Open database: {dbpath}')
        self._database = BudgyDatabase(dbpath)
        self.update_database_status()

    def update_database_status(self):
        records = self._database.all_records()
        self.top_panel.set_record_count(len(records))
        start, end = self._database.get_date_range()
        self.top_panel.set_data_range(start, end)
        self.function_panel.data_panel.set_data(records)

    def handle_event(self, event):
        if super().handle_event(event):
            return True
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._quit_button:
                self.is_running = False
                self.on_shutdown()
                pygame.quit()
                return True
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.top_panel.drop_down_menu:
                print(f'New Function: {event.text}')
                if event.text == 'Report Functions':
                    self.function_panel.show_subpanel('report')
                    self.message_panel.info('Showing Report Panel')
                    return True
                if event.text == 'Data Functions':
                    self.function_panel.show_subpanel('data')
                    self.message_panel.error('Showing Data Panel')
                    return True
                if event.text == 'Exit':
                    self.is_running = False
                    self.on_shutdown()
                    pygame.quit()
                    return True

                raise Exception(f'Bad Dropdown Function Item: {event.text}')

        elif event.type == SELECT_DATABASE:
            print(f'select database {event}')
            dialog = UIFileDialog(
                pygame.Rect(0, 0, 800, 600),
                self.ui_manager,
                'Select Database File',
                initial_file_path=event.db_path,
                object_id='#database_dialog',
                allow_existing_files_only=False
            )
        elif event.type == OPEN_DATABASE:
            print(f'load database: {event.db_path}')
            #self.open_database(event.db_path)
        elif event.type == budgy.gui.events.DATA_SOURCE_CONFIRMED:
            post_show_message(f'Loading OFX data from {event.path}')
            records = load_ofx_file(event.path)
            post_show_message(f'Merging imported records')
            self._database.merge_records(records)
            self.update_database_status()
            post_clear_messages()
            return True
        elif event.type == budgy.gui.events.DELETE_ALL_DATA_CONFIRMED:
            print(f'DELETING ALL DATA FROM DATABASE')
            self._database.delete_all_records()
            self.update_database_status()
            return True


    def _parse_args(self):
        parser = argparse.ArgumentParser(self._title)
        parser.add_argument('--db', type=Path, help='Path to sqlite3 database. Will be created if it '
                                                                   'does not exist')
        return parser.parse_args()

def main():
    app = BudgyViewerApp()
    app.setup()
    app.run()

if __name__ == '__main__':
    main()
