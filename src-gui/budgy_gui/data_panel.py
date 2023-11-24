from pathlib import Path

import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIPanel, UILabel, UIButton, UITextEntryLine, UIProgressBar
from pygame.event import custom_type

from budgy.database import BudgyDatabase

OPEN_DATABASE = custom_type()
LOAD_DATA_SOURCE = custom_type()
SELECT_DATABASE = custom_type()
SELECT_SOURCE_FILE = custom_type()

class DataPanel(UIPanel):
    PROGRESS_LABEL_WIDTH = 175
    PROGRESS_BAR_WIDTH = 500
    def __init__(self, config_in, *args, **kwargs):
        self.budgy_config:dict = config_in
        super().__init__(*args, **kwargs)
        self._button_width = 130
        self._button_height = 35
        self._open_db_button = UIButton(
            pygame.Rect(0, 0, self._button_width, self._button_height),
            'Open Database',
            self.ui_manager,
            container=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'left'
            }
        )
        x = self._open_db_button.get_relative_rect().right
        y = self._open_db_button.get_relative_rect().top
        w = self.get_relative_rect().width - (self._button_width * 2)
        h = self._open_db_button.get_relative_rect().height
        self._db_path_item = UITextEntryLine(
            pygame.Rect(x, y, w, h),
            self.ui_manager,
            container=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'right'
            }
        )
        self._db_path_item.set_text(self.database_path)
        x = -self._button_width #  self._db_path_item.get_relative_rect().right
        w = self._button_width
        self._select_db_button = UIButton(
            pygame.Rect(x, y, w, h),
            'Select DB',
            self.ui_manager,
            container=self,
            anchors={
                'top': 'top', 'left': 'right',
                'bottom': 'top', 'right': 'right'
            }
        )
        y += self._button_height
        x = 0
        w = self.get_relative_rect().width
        self._record_count_item = UILabel(
            pygame.Rect(x, y, w, h),
            'Database Not Open', self.ui_manager,
            container=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'right'
            },
            object_id=ObjectID(class_id='@bold',
                               object_id='#data-label')
        )
        y += self._button_height
        x = 0
        w = self._button_width
        self._load_data_button = UIButton(
            pygame.Rect(x, y, w, h), "Import Data",
            self.ui_manager, container=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'left'
            }
        )
        self._load_data_button.disable()
        x = self._load_data_button.get_relative_rect().width
        w = self.get_relative_rect().width - (self._button_width * 2)
        self._apple_data_file_item = UITextEntryLine(
            pygame.Rect(x, y, w, h),
            self.ui_manager,
            container=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'right'
            }
        )
        self._apple_data_file_item.set_text(self.data_source_path)
        x = -self._button_width #  self._db_path_item.get_relative_rect().right
        w = self._button_width
        self._select_data_button = UIButton(
            pygame.Rect(x, y, w, h),
            'Select File',
            self.ui_manager,
            container=self,
            anchors={
                'top': 'top', 'left': 'right',
                'bottom': 'top', 'right': 'right'
            }
        )
        y += self._button_height
        x = 0
        w = self.get_relative_rect().width
        self._xml_read_progress_text = UILabel(
            pygame.Rect(x, y, w, h),
            '',
            self.ui_manager,
            container=self,
            anchors={'top': 'top', 'left': 'left',
                     'bottom': 'top', 'right': 'left'},
            object_id=ObjectID(class_id='@vert-centered',
                               object_id='#data-label')
        )

        y += self._button_height
        x = 0
        w = DataPanel.PROGRESS_LABEL_WIDTH
        poff = 8 # why?
        self.xml_record_load_label = UILabel(
            pygame.Rect(x, y, w, h),
            "Loading Records: ",
            self.ui_manager,
            container=self,
            anchors={'top': 'top', 'left': 'left',
                     'bottom': 'top', 'right': 'left'},
            visible=0,
            object_id=ObjectID('@vert-centered',
                               '#progress-label')
        )
        x = self.xml_record_load_label.get_relative_rect().right
        w = self.get_relative_rect().width - self.xml_record_load_label.get_relative_rect().width
        self.xml_record_load_progress = UIProgressBar(
            pygame.Rect(x, self.xml_record_load_label.get_relative_rect().bottom + poff, DataPanel.PROGRESS_BAR_WIDTH, h), self.ui_manager,
            container=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'left'
            },
            visible=0
        )
        y += self._button_height
        x = 0
        w = DataPanel.PROGRESS_LABEL_WIDTH
        self.xml_record_save_label = UILabel(
            pygame.Rect(x, y, w, h),
            'Saving Records:',
            self.ui_manager,
            container=self,
            anchors={'top': 'top', 'left': 'left',
                     'bottom': 'top', 'right': 'left'},
            visible=0,
            object_id=ObjectID('@vert-centered',
                               '#progress-label')
        )
        x = self.xml_record_save_label.get_relative_rect().right
        w = self.get_relative_rect().width - self.xml_record_save_label.get_relative_rect().width
        self.xml_record_save_progress = UIProgressBar(
            pygame.Rect(x, self.xml_record_save_label.get_relative_rect().bottom + poff, DataPanel.PROGRESS_BAR_WIDTH, h), self.ui_manager,
            container=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'left'
            },
            visible=0
        )

        self.database_path = self.budgy_config['database']['path']
        self.db = BudgyDatabase(Path(self.database_path).expanduser())

        # self._file_path = '/Users/mark/git/healthdata/export.xml'
        self.data_source_path = '' # /export.zip'

    def start_reading_data(self):
        self._xml_read_progress_text.show()
        self.xml_record_load_label.set_text('Loading Data')
        self.set_xml_total_records(0)

    def finish_reading_data(self):
        self.xml_record_load_label.set_text('Parsing Records:')

    def set_xml_total_records(self, t):
        self.xml_record_load_progress.maximum_progress = t
        self.xml_record_load_progress.percent_full = 0
        self.xml_record_load_progress.update(0)

    def set_xml_load_progress(self, p):
        self.xml_record_load_label.show()
        self.xml_record_load_progress.show()
        self.xml_record_load_progress.set_current_progress(p)
        pct = p / self.xml_record_load_progress.maximum_progress * 100.0 \
            if self.xml_record_load_progress.maximum_progress > 0 else 0
        self.xml_record_load_progress.percent_full = pct
        self.xml_record_load_progress.update(0)

    def set_database_total_records(self, t):
        self.xml_record_save_progress.maximum_progress = t
        self.xml_record_save_progress.percent_full = 0
        self.xml_record_save_progress.update(0)

    def set_database_save_progress(self, p):
        self.xml_record_save_label.show()
        self.xml_record_save_progress.show()
        self.xml_record_save_progress.set_current_progress(p)
        pct = p / self.xml_record_save_progress.maximum_progress * 100.0 \
            if self.xml_record_save_progress.maximum_progress > 0 else 0
        self.xml_record_save_progress.percent_full = pct
        self.xml_record_save_progress.update(0)

    @property
    def database_path(self):
        return self._db_path_item.get_text()

    @database_path.setter
    def database_path(self, p):
        self._db_path_item.set_text(p)

    @property
    def data_source_path(self):
        return self._apple_data_file_item.get_text()

    @data_source_path.setter
    def data_source_path(self, p):
        self._apple_data_file_item.set_text(p)

    def set_number_of_records_text(self, n):
        if isinstance(n, int):
            self._record_count_item.set_text(f'{n} Records')
        else:
            self._record_count_item.set_text(n)

    def set_database_is_open(self, is_open):
        if is_open:
            self._load_data_button.enable()
        else:
            self._load_data_button.disable()

    def process_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._open_db_button:
                print('OPEN DB')
                event_data = {
                    'db_path': self.database_path
                }
                pygame.event.post(pygame.event.Event(OPEN_DATABASE, event_data))
                return True
            elif event.ui_element == self._select_db_button:
                print('SELECT DB')
                event_data = {
                    'db_path': self.database_path
                }
                pygame.event.post(pygame.event.Event(SELECT_DATABASE, event_data))
                return True
            elif event.ui_element == self._select_data_button:
                event_data = {
                    'file_path': self.data_source_path
                }
                pygame.event.post(pygame.event.Event(SELECT_SOURCE_FILE, event_data))
                return True
            elif event.ui_element == self._load_data_button:
                event_data = { 'file_path': self.data_source_path }
                pygame.event.post(pygame.event.Event(LOAD_DATA_SOURCE, event_data))
                return True
        return False
