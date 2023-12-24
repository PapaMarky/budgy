import budgy.gui
import pygame
from pygame_gui.elements import UIPanel, UILabel, UIDropDownMenu
from pygame_gui.core import ObjectID
from dateutils import relativedelta
from datetime import datetime

from budgy.gui.configdata import BudgyConfig

class TopPanel(UIPanel):
    LABLE_WIDTH = 100
    TEXT_WIDTH = 175
    DROP_DOWN_WIDTH = 200
    def __init__(self, config_in:BudgyConfig, *args, **kwargs):
        self.budgy_config:BudgyConfig = config_in
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
        self.set_data_range(None, None)

        y += budgy.gui.MARGIN + budgy.gui.BUTTON_HEIGHT
        label3 = UILabel(
            pygame.Rect(0, y, self.TEXT_WIDTH, budgy.gui.BUTTON_HEIGHT),
            'Retirement:',
            self.ui_manager,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'left'
            },
            container=self,
            object_id=ObjectID(class_id='#data-label',
                               object_id='@bold-16')

        )
        self.retirement_info = UILabel(
            pygame.Rect(x, y, w, budgy.gui.BUTTON_HEIGHT),
            '',
            self.ui_manager,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'right'
            },
            container=self,
            object_id=ObjectID(class_id='#data-text')
        )
        self.set_retirement_info(None)

        # Add: Function DropDown
        data_function_option = 'Data Functions'
        report_function_option = 'Report Functions'
        option_list = [
            data_function_option,
            report_function_option,
            'Exit'
        ]
        w = self.DROP_DOWN_WIDTH
        x = (self.relative_rect.width - (w + budgy.gui.MARGIN))
        x = -(w + budgy.gui.MARGIN)
        y = label1.get_abs_rect().y
        h = budgy.gui.BUTTON_HEIGHT
        rr = pygame.Rect(x, y, w, h)
        # rect.topright = (budgy.gui.BUTTON_HEIGHT, budgy.gui.MARGIN)
        self.drop_down_menu = UIDropDownMenu(
            option_list,
            data_function_option,
            rr,
            manager=self.ui_manager,
            container=None,
            anchors={
                'top': 'top',
                # 'left': 'right',
                # 'bottom': 'top',
                'right': 'right'
            },
            expansion_height_limit  = (4 * budgy.gui.BUTTON_HEIGHT)
        )

    def set_record_count(self, count):
        self.nrecords_field.set_text(f'{count}')

    def set_data_range(self, first_date:datetime, last_date:datetime):
        if first_date is None:
            self.date_range_field.set_text('No Data')
            return
        start_date = first_date.strftime('%Y-%m-%d')
        end_date = last_date.strftime('%Y-%m-%d')
        self.date_range_field.set_text(f'{start_date} - {end_date}')

    def set_retirement_info(self, target_date):
        if target_date is None:
            self.retirement_info.set_text('')
            return

        target_date = datetime.strptime(target_date, '%Y/%m/%d')
        today = datetime.today()

        delta = relativedelta(target_date, today)

        year_str = ''
        month_str = ''
        day_str = ''
        if delta.years > 0:
            year_str = f'{delta.years} years '

        if delta.months > 0:
            month_str = f'{delta.months} months '

        if delta.days > 0:
            day_str = f'{delta.days} days'

        self.retirement_info.set_text(f'{year_str}{month_str}{day_str}')