import budgy.gui
import pygame
from pygame_gui.elements import UIPanel, UILabel
from pygame_gui.core import ObjectID

class TopPanel(UIPanel):
    LABLE_WIDTH = 100
    TEXT_WIDTH = 500
    def __init__(self, config_in, *args, **kwargs):
        self.budgy_config:dict = config_in
        super().__init__(*args, **kwargs)
        # Add: Records: NNNNNN
        y = budgy.gui.MARGIN
        label1 = UILabel(
            pygame.Rect(0, y, self.TEXT_WIDTH, budgy.gui.BUTTON_HEIGHT),
            'Record Count:',
            self.ui_manager,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'right'
            },
            container=self,
            object_id=ObjectID(class_id='@data-label',
                               object_id='@bold')
        )
        y += budgy.gui.MARGIN + budgy.gui.BUTTON_HEIGHT
        # Add: Data Range: YYYY-MM-DD to YYYY-MM-DD
        label2 = UILabel(
            pygame.Rect(0, y, self.TEXT_WIDTH, budgy.gui.BUTTON_HEIGHT),
            'Data Range:',
            self.ui_manager,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'right'
            },
            container=self,
            object_id=ObjectID(class_id='@data-label',
                               object_id='@bold')
        )


        # Add: Function DropDown

    def set_record_count(self, count):
        pass

    def set_data_range(self, first_date, last_date):
        pass