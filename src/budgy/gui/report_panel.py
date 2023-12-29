from typing import Dict, Union

import pygame
from pygame import event as pygame_event
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UILabel, UIButton
import budgy.gui.constants
from budgy.core.database import BudgyDatabase
from budgy.gui.function_panel import BudgyFunctionSubPanel

EXPENSE_DETAILS_REQUEST = pygame_event.custom_type()

class ExpenseDetailButton(UIButton):
    def __init__(self, year, month, *args, **kwargs):
        self.year = year
        self.month = month
        super().__init__(*args, **kwargs)

    def process_event(self, event: pygame.event.Event) -> bool:
        event_consumed = super().process_event(event)
        if not event_consumed:
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if isinstance(event.ui_element, ExpenseDetailButton):
                    print(f'Expense Button: {event.ui_element.year} - {event.ui_element.month}')
                    event_data = {
                        'year': event.ui_element.year,
                        'month': event.ui_element.month
                    }
                    pygame.event.post(pygame.event.Event(EXPENSE_DETAILS_REQUEST, event_data))
                    event_consumed = True
        return event_consumed


class BudgyReportPanel(BudgyFunctionSubPanel):
    def __init__(self, config_in, function_panel, *args, **kwargs):
        super().__init__(config_in, function_panel, *args, **kwargs)

        self.database:BudgyDatabase = None

    def set_database(self, database:BudgyDatabase):
        self.database = database
        self.create_table()

    def create_table(self):
        # table headers
        column_headers = (
            '', 'Ave', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        )
        ncolumns = len(column_headers)
        column_width = self.relative_rect.width / ncolumns
        column0_width = column_width - 12
        column_height = budgy.gui.constants.BUTTON_HEIGHT
        x = 0
        y = 0

        for header in column_headers:
            if header != '':
                UILabel(
                    pygame.Rect(x, y, column_width - 1, column_height),
                    header,
                    container=self,
                    object_id=ObjectID(class_id='#label', object_id='@label-center'),
                    anchors={
                        'top': 'top', 'left': 'left',
                        'bottom': 'top', 'right': 'right'
                    }
                )
            if header != '':
                x += column_width + 1
            else:
                x += column0_width + 1
        y += column_height + 1

        report_data = self.database.get_report()

        d = {}
        for row in report_data:
            year = row['year']
            monthly_expense = int(row['month']) - 1
            value = row['expenses']
            if year not in d:
                d[year] = [None, None, None, None, None, None, None, None, None, None, None, None]
            d[year][monthly_expense] = f'{value:9.0f}'

        for year in sorted(d):
            x = 0
            UILabel(
                pygame.Rect(x, y, column0_width - 1, column_height),
                year,
                container=self,
                object_id=ObjectID(class_id='#label', object_id='@label-center'),
                anchors={
                    'top': 'top', 'left': 'left',
                    'bottom': 'top', 'right': 'right'
                }
            )
            x += column0_width + 1

            sum = 0
            n = 0
            for monthly_expense in d[year]:
                if monthly_expense is not None:
                    sum += float(monthly_expense)
                    n += 1
            average = sum/n
            ExpenseDetailButton(
                year, None,
                pygame.Rect(x, y, column_width - 1, column_height),
                f'{average:.0f}',
                container=self,
                anchors={
                    'top': 'top', 'left': 'left',
                    'bottom': 'top', 'right': 'right'
                },
                object_id=ObjectID(class_id='#average-button')
            )
            x += column_width + 1

            month = 0
            for monthly_expense in d[year]:
                month += 1
                if monthly_expense is not None:
                    ExpenseDetailButton(
                        year, f'{month:02d}',
                        pygame.Rect(x, y, column_width - 1, column_height),
                        f'{float(monthly_expense):.0f}',
                        container=self,
                        anchors={
                            'top': 'top', 'left': 'left',
                            'bottom': 'top', 'right': 'right'
                        },
                        object_id=ObjectID(class_id='#average-button')
                    )
                x += column_width + 1
            y += column_height + 1

    def process_event(self, event: pygame.event.Event) -> bool:
        if event.type == EXPENSE_DETAILS_REQUEST:
            print(f'Expense Details for {event.year}-{event.month}')