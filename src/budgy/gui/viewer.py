import argparse
import glob
import logging
import logging.handlers
import os.path
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
        self._setup_logging()
        themes_file = budgy.gui.get_themes_file_path('theme.json')
        logging.info(f'themes file: {themes_file}')
        if themes_file:
            self._ui_manager.get_theme().load_theme(themes_file)
        else:
            logging.warning('theme file not found')
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

        # Once the database is open, pass it to the report panel. (this all need to be thought out better)
        self.function_panel.set_database(self._database)

    def open_database(self):
        dbpath = Path(self.database_path).expanduser()
        logging.info(f'Open database: {dbpath}')
        self._database = BudgyDatabase(dbpath)
        self.update_database_status()

    def update_database_status(self):
        records = self._database.all_records()
        self.top_panel.set_record_count(len(records))
        start, end = self._database.get_date_range()
        self.top_panel.set_data_range(start, end)

        # TODO: BudgyFunctionalPanel should have a "update_database_status"
        self.function_panel.data_panel.set_data(records)
        self.function_panel.report_panel.rebuild_report()

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
                logging.debug(f'New Function: {event.text}')
                if event.text == 'Report Functions':
                    self.function_panel.show_subpanel('report')
                    self.function_panel.report_panel.render_data()
                    return True
                if event.text == 'Data Functions':
                    self.function_panel.show_subpanel('data')
                    self.function_panel.data_panel.render_data()
                    return True
                if event.text == 'Exit':
                    self.is_running = False
                    self.on_shutdown()
                    pygame.quit()
                    return True

                raise Exception(f'Bad Dropdown Function Item: {event.text}')

        elif event.type == SELECT_DATABASE:
            logging.debug(f'select database {event}')
            dialog = UIFileDialog(
                pygame.Rect(0, 0, 800, 600),
                self.ui_manager,
                'Select Database File',
                initial_file_path=event.db_path,
                object_id='#database_dialog',
                allow_existing_files_only=False
            )
        elif event.type == OPEN_DATABASE:
            logging.info(f'load database: {event.db_path}')
            #self.open_database(event.db_path)
        elif event.type == budgy.gui.events.DATA_SOURCE_CONFIRMED:
            files = []
            if os.path.isdir(event.path):
                all_files = glob.glob(event.path + '/*')
                logging.warning(f'ALL FILES: {all_files}')
                for file in all_files:
                    if file.endswith('.ofx') or file.endswith('.qfx'):
                        files.append(file)
                        logging.debug(f'FILE: {file}')
            else:
                files.append(event.path)
                logging.debug(f'FILE: {event.path}')
            for file in files:
                msg = f'Loading OFX data from {file}'
                post_show_message(msg)
                logging.info(msg)
                records = load_ofx_file(file)
                post_show_message(f'Merging {len(records)} imported records')
                self._database.merge_records(records)
                self.update_database_status()
                post_clear_messages()
            return True
        elif event.type == budgy.gui.events.DELETE_ALL_DATA_CONFIRMED:
            logging.warn('DELETING ALL DATA FROM DATABASE')
            self._database.delete_all_records()
            self.update_database_status()
            return True
        elif event.type == budgy.gui.events.CATEGORY_CHANGED:
            self.update_database_status()
            return False

    def _parse_args(self):
        parser = argparse.ArgumentParser(self._title)
        parser.add_argument('--db', type=Path, help='Path to sqlite3 database. Will be created if it '
                                                                   'does not exist')
        parser.add_argument(
            '--log-level',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            default='INFO',
            help='Set the logging level (default: INFO)'
        )
        parser.add_argument(
            '--log-dir',
            type=Path,
            default=Path.home() / '.config' / 'budgy' / 'logs',
            help='Set the log directory (default: ~/.config/budgy/logs/)'
        )
        parser.add_argument(
            '--log-console',
            action='store_true',
            help='Log to both file and console'
        )
        return parser.parse_args()

    def _setup_logging(self):
        """
        Configure logging based on command line arguments.
        Sets up file logging with rotation and optional console logging.
        """
        # Ensure log directory exists
        log_dir = self._args.log_dir
        log_dir.mkdir(parents=True, exist_ok=True)

        # Configure logging level
        log_level = getattr(logging, self._args.log_level.upper())

        # Set up formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # Clear any existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Set up file logging with rotation (3 files, 3KB each)
        log_file = log_dir / f'{self._title.lower().replace(" ", "-").replace(":", "")}.log'
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=3 * 1024,  # 3KB
            backupCount=2,      # Keep 2 backup files (total of 3 files)
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

        # Set up console logging if requested
        if self._args.log_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)

        # Log the configuration
        logging.info(f'Logging configured: level={self._args.log_level}, file={log_file}, console={self._args.log_console}')

    def run(self):
        try:
            super().run()
        except Exception as e:
            logging.exception(f'UNHANDLED EXEPTION: {e}')
            raise e


def main():
    app = BudgyViewerApp()
    app.setup()
    app.run()


if __name__ == '__main__':
    main()