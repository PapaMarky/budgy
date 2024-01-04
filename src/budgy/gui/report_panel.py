from typing import Dict, Union, List

import pygame
from pygame import event as pygame_event
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UILabel, UIButton, UIPanel
import budgy.gui.constants
from budgy.core.database import BudgyDatabase
from budgy.gui.events import TOGGLE_BUTTON, post_show_message
from budgy.gui.function_panel import BudgyFunctionSubPanel
from budgy.gui.constants import MARGIN, BUTTON_HEIGHT
from budgy.gui.record_view_panel import RecordViewPanel

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
        # put all labels and buttons in one place so we can destroy them when we rebuild
        self.header_labels = []
        self.row_items = {}
        self.detail_y = 0
        self.detail_panel:UIPanel = None
        self.detail_rows:List[Dict] = []
        self.detail_record_view:RecordViewPanel = None

    def set_database(self, database:BudgyDatabase):
        self.database = database
        self.create_summary_table()

    def rebuild_report(self):
        if self.database is not None:
            self.clear_report()
            self.create_summary_table()

    def clear_report(self):
        for label in self.header_labels:
            label.kill()
        for year in self.row_items:
            self.row_items[year]['label'].kill()
            for button in self.row_items[year]['buttons']:
                if button is not None:
                    button.kill()
        self.header_labels = []
        self.row_items = {}

    def create_summary_table(self):
        # table headers
        column_headers = (
            '', 'Ave', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        )
        ncolumns = len(column_headers)
        column_width = self.relative_rect.width / ncolumns
        column0_width = column_width - 12
        column_height = BUTTON_HEIGHT
        x = 0
        y = 0

        for header in column_headers:
            if header != '':
                label = UILabel(
                    pygame.Rect(x, y, column_width - 1, column_height),
                    header,
                    container=self,
                    object_id=ObjectID(class_id='#label', object_id='@label-center'),
                    anchors={
                        'top': 'top', 'left': 'left',
                        'bottom': 'top', 'right': 'left'
                    }
                )
                self.header_labels.append(label)
            if header != '':
                x += column_width + 1
            else:
                x += column0_width + 1
        y += column_height + 1

        report_data = self.database.get_report()

        for year in sorted(report_data):
            if year not in self.row_items:
                self.row_items[year] = {
                    'label': None,
                    'buttons': [],
                }
            x = 0
            year_label = UILabel(
                pygame.Rect(x, y, column0_width - 1, column_height),
                year,
                container=self,
                object_id=ObjectID(class_id='#label', object_id='@label-center'),
                anchors={
                    'top': 'top', 'left': 'left',
                    'bottom': 'top', 'right': 'left'
                }
            )
            year_label.set_tooltip(f'<b><center>{year}</center></b><br/>'
                                   f'<b>Min: </b>{report_data[year]["minimum"]:.0f}<br/>'
                                   f'<b>Max: </b>{report_data[year]["maximum"]:.0f}<br/>'
                                   f'<b>Ave: </b>{report_data[year]["average"]:.0f}')
            self.row_items[year]['label'] = year_label
            x += column0_width + 1

            average = report_data[year]['average']
            button = ExpenseDetailButton(
                year, None,
                pygame.Rect(x, y, column_width - 1, column_height),
                f'{abs(average):.0f}',
                container=self,
                anchors={
                    'top': 'top', 'left': 'left',
                    'bottom': 'top', 'right': 'left'
                },
                object_id=ObjectID(class_id='#average-button')
            )
            self.row_items[year]['buttons'].append(button)
            x += column_width + 1

            month = 0
            for monthly_expense in report_data[year]['months']:
                month += 1
                button = None
                if monthly_expense is not None:
                    button = ExpenseDetailButton(
                        year, f'{month:02d}',
                        pygame.Rect(x, y, column_width - 1, column_height),
                        f'{abs(float(monthly_expense)):.0f}',
                        container=self,
                        anchors={
                            'top': 'top', 'left': 'left',
                            'bottom': 'top', 'right': 'left'
                        },
                        object_id=ObjectID(class_id='#average-button')
                    )
                self.row_items[year]['buttons'].append(button)
                x += column_width + 1
            y += column_height + 1
        self.detail_y = y

    def update_summary_table(self):
        report_data = self.database.get_report()
        for year in report_data:
            if year in self.row_items:
                average = report_data[year]['average']
                self.row_items[year]['buttons'][0].set_text(f'{abs(average):.0f}')
                for month in range(12):
                    expense = report_data[year]['months'][month]
                    if expense is not None:
                        month_item = self.row_items[year]['buttons'][month+1] # add one to skip monthly average
                        if month_item is not None:
                            month_item.set_text(f'{abs(float(expense)):.0f}')
                        else:
                            post_show_message(f'ERROR: Month {year}/{month} not found in summary table', 'error')
            else:
                post_show_message(f'ERROR: Year {year} not found in summary table', 'error')


    def render_data(self):
        if self.detail_record_view is not None:
            self.detail_record_view.render_data()

    def create_detail_report(self, year, month):
        if self.detail_panel is not None:
            self.detail_panel.kill()

        x = 0
        y = self.detail_y
        w = self.relative_rect.width - 4 * MARGIN
        h = self.relative_rect.height - self.detail_y - 4 * MARGIN
        self.detail_panel = UIPanel(
            pygame.Rect(0, y, w, h),
            container=self, parent_element=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'bottom', 'right': 'right'
            },
            object_id=ObjectID(class_id='#report-detail-panel')
        )
        x = 0
        y = 0
        w = self.detail_panel.relative_rect.width - 4 * MARGIN
        h = BUTTON_HEIGHT
        label_text = ''
        if month is not None:
            label_text = f'{year}-{month} Monthly Expense Details'
        else:
            label_text = f'{year} Yearly Expense Details'
        detail_label = UILabel(
            pygame.Rect(x, y, w, h),
            label_text,
            container=self.detail_panel,
            object_id=ObjectID(class_id='#label', object_id='@label-left'),
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'left'
            }
        )
        self.detail_rows = self.database.all_records(year=year, month=month)
        print(f'Got {len(self.detail_rows)} records')
        y += h + MARGIN
        h = self.detail_panel.relative_rect.height - y - 2 * MARGIN
        self.detail_record_view = RecordViewPanel(
            pygame.Rect(x, y, w, h),
            manager=self.ui_manager,
            container=self.detail_panel,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'bottom', 'right': 'right'
            },
            object_id=ObjectID(object_id='#records_view_panel')
        )
        self.detail_record_view.set_data(self.detail_rows)

    def process_event(self, event: pygame.event.Event) -> bool:
        event_consumed = super().process_event(event)
        if not event_consumed:
            if event.type == EXPENSE_DETAILS_REQUEST:
                self.create_detail_report(event.year, event.month)
            elif event.type == TOGGLE_BUTTON:
                fitid = event.user_data["fitid"]
                self.database.exclude_fitid(fitid, event.state)
                # event_consumed = True
                self.update_summary_table()
        return event_consumed
