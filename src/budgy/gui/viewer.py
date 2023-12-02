import argparse
from pathlib import Path

import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.windows import UIFileDialog, UIMessageWindow
from pygame_gui_extras.app import GuiApp
from pygame_gui.elements import UIPanel, UIButton

from budgy.core.database import BudgyDatabase
from budgy.version import __version__ as package_version

import budgy.gui

from budgy.gui.data_panel import DataPanel
from budgy.gui.top_panel import TopPanel
from budgy.gui.configdata import BudgyConfig
from budgy.gui.events import SELECT_DATABASE, OPEN_DATABASE

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
        self._button_rect = pygame.Rect(0, 0, budgy.gui.BUTTON_WIDTH, budgy.gui.BUTTON_HEIGHT)
        self._database:BudgyDatabase = None
        self._config = BudgyConfig()

    @property
    def database_path(self):
        return self._config.config_dict['database']['path']

    def setup(self):
        tp_height = (2 * budgy.gui.BUTTON_HEIGHT) + (6 * budgy.gui.MARGIN)
        self.top_panel = TopPanel(
            self._config.config_dict,
            pygame.Rect(0, 0,
                        self.size[0], tp_height),
            1,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'right'
            },
            margins={'top': budgy.gui.MARGIN, 'left': budgy.gui.MARGIN,
                     'bottom': budgy.gui.MARGIN, 'right': budgy.gui.MARGIN},
            manager=self.ui_manager,
            object_id=ObjectID(class_id='#top-panel')
        )

    def xxxx(self):
        self._data_panel = DataPanel(
            self._config.config_dict,
            pygame.Rect(0, self.top_panel.get_relative_rect().bottom,
                        self.size[0], self.size[1] - self.top_panel.get_relative_rect().height),
            1,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'bottom', 'right': 'right'
            },
            manager=self.ui_manager,
        )

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._quit_button:
                self.is_running = False
                self.on_shutdown()
                pygame.quit()
                return True
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.top_panel.drop_down_menu:
                print(f'New Function: {event.text}')
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
            #self._data_panel.disable()
            #self._report_panel.disable()
        elif event.type == OPEN_DATABASE:
            print(f'load database: {event.db_path}')
            #self.open_database(event.db_path)

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
