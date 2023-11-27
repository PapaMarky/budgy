import budgy.gui
import pygame
from pygame_gui.elements import UIPanel, UILabel
from pygame_gui.core import ObjectID
from datetime import datetime

class TopPanel(UIPanel):
    LABLE_WIDTH = 100
    TEXT_WIDTH = 175
    def __init__(self, config_in, *args, **kwargs):
        self.budgy_config:dict = config_in
        super().__init__(*args, **kwargs)
        # Add: Records: NNNNNN
        y = budgy.gui.MARGIN
        x = budgy.gui.MARGIN
        label1 = UILabel(
            pygame.Rect(0, y, self.TEXT_WIDTH, budgy.gui.BUTTON_HEIGHT),
            'Record Count:',
            self.ui_manager,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'left'
            },
            container=self,
            object_id=ObjectID(class_id='#data-label',
                               object_id='@bold-16')
        )
        w = self.relative_rect.width - label1.relative_rect.width
        x = self.TEXT_WIDTH + budgy.gui.MARGIN
        self.nrecords_field = UILabel(
            pygame.Rect(x, y, w, budgy.gui.BUTTON_HEIGHT),
            'No Database',
            self.ui_manager,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'right'
            },
            container=self,
            object_id=ObjectID(class_id='#data-text')
        )
        y += budgy.gui.MARGIN + budgy.gui.BUTTON_HEIGHT
        # Add: Data Range: YYYY-MM-DD to YYYY-MM-DD
        label2 = UILabel(
            pygame.Rect(0, y, self.TEXT_WIDTH, budgy.gui.BUTTON_HEIGHT),
            'Data Range:',
            self.ui_manager,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'left'
            },
            container=self,
            object_id=ObjectID(class_id='#data-label',
                               object_id='@bold-16')
        )
        self.date_range_field = UILabel(
            pygame.Rect(x, y, w, budgy.gui.BUTTON_HEIGHT),
            'YYYY-MM-DD to YYYY-MM-DD',
            self.ui_manager,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'right'
            },
            container=self,
            object_id=ObjectID(class_id='#data-text')
        )

        self.set_data_range(datetime.now(), datetime.now())

        # Add: Function DropDown


    def set_record_count(self, count):
        self.nrecords_field.set_text(f'{count}')

    def set_data_range(self, first_date:datetime, last_date:datetime):
        start_date = first_date.strftime('%Y-%m-%d')
        end_date = last_date.strftime('%Y-%m-%d')
        self.date_range_field.set_text(f'{start_date} - {end_date}')