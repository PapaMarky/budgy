import datetime
import math
import re
from pathlib import Path
from typing import List
import pygame

from pygame_gui.core import ObjectID
from pygame_gui.elements import UIPanel, UIVerticalScrollBar, UILabel

import budgy.gui.constants
from budgy.core.database import BudgyDatabase
from budgy.gui.category_button import CategoryButton
from budgy.gui.db_record_view_panel import DbRecordView
from budgy.gui.toggle_button import ToggleButton, TOGGLE_BUTTON

from budgy.gui.events import post_show_message, CATEGORY_CHANGED


class RecordView(DbRecordView):
    RECURRING_EXPENSE_COLOR = 'mediumseagreen'
    ONE_TIME_EXPENSE_COLOR = 'seagreen'
    NON_EXPENSE_COLOR = 'slategrey'
    # TODO: this level of abstraction just makes it impossible to follow what is going on. SIMPLIFY THIS
    #       Make it a functional Interface?
    my_field_names = (
        'fitid',
        'account',
        'type',
        'posted',
        'amount',
        'name',
        'memo',
        'checknum',
        'category'
    )
    my_field_defs = {
        'posted': {
            'position': 0,
            'width': 100,
            'oid': ObjectID(class_id='@record-field')
        },
        'amount': {
            'position': 1,
            'width': 100,
            'oid': ObjectID(class_id='@record-field', object_id='#field-right')
        },
        'name': {
            'position': 2,
            'width': 270,
            'oid': ObjectID(class_id='@record-field', object_id='#field-left')
        },
        'memo': {
            'position': 3,
            'width': 400,
            'oid': ObjectID(class_id='@record-field', object_id='#field-left')
        },
        'category': {
            'position': 4,
            'width': 300,
            'oid': ObjectID(class_id='@record-button', object_id='#field-button')
        }
    }

    def __init__(self, database:BudgyDatabase, *args, **kwargs):
        kwargs.__setitem__('object_id',
                           ObjectID(class_id='@record-view-panel'))
        self._outer_record = None

        self._category_button:CategoryButton = None
        super().__init__(database, self.my_field_names, self.my_field_defs, *args, **kwargs)

    def build_items(self):
        layer = 1
        x = 0
        for f in self.field_defs:
            w = self.field_defs[f]['width']
            oid = self.field_defs[f]['oid']
            item = None
            if f == 'category':
                item = CategoryButton(
                    self._database,
                    pygame.Rect(x, 0, w, self.RECORD_VIEW_HEIGHT),
                    'category',
                    container=self, parent_element=self,
                    object_id=oid,
                    anchors={
                        'top': 'top', 'left': 'left',
                        'bottom': 'bottom', 'right': 'left'
                    }
                )
                item.disable()
                self._category_button = item
            else:
                item = UILabel(
                    pygame.Rect(x, 0, w, self.RECORD_VIEW_HEIGHT),
                    '',
                    container=self, parent_element=self,
                    object_id=oid,
                    anchors={
                        'top': 'top', 'left': 'left',
                        'bottom': 'bottom', 'right': 'left'
                    }
                )
            x += w + 1
            self._fields.append(item)

    def set_record(self, record):
        self._outer_record = record
        if record is None:
            self._category_button.disable()
            self._category_button.hide()
            self.set_color(self.NON_EXPENSE_COLOR)
        else:
            self._category_button.enable()
            if self.visible:
                self._category_button.show()
                self._category_button.set_category_text()
                self._category_button.txn_name = record['name']

        for field in self.field_names:
            if record is None:
                self._record[field] = ''
            else:
                if not field in record:
                    raise Exception(f'Field missing from record: {field}')
                self._record[field] = record[field]
            if field in self.field_defs:
                i = self.field_defs[field]['position']
                value = str(self._record[field])
                if field == 'amount' and isinstance(value, float):
                    value = f'{float(value):8.02f}'
                elif field == 'posted':
                    value = value[:10]
                elif field == 'category':
                    if record is None:
                        self._fields[i].fitid = None
                    else:
                        self._fields[i].fitid = self._record['fitid']
                    if self.visible:
                        if self._fields[i].expense_type == BudgyDatabase.RECURRING_EXPENSE_TYPE:
                            self.set_color(self.RECURRING_EXPENSE_COLOR)
                        elif self._fields[i].expense_type == BudgyDatabase.ONE_TIME_EXPENSE_TYPE:
                            self.set_color(self.ONE_TIME_EXPENSE_COLOR)
                        else:
                            self.set_color(self.NON_EXPENSE_COLOR)
                if field != 'category':
                    self._fields[i].set_text(str(value))

    def process_event(self, event: pygame.event.Event) -> bool:
        event_consumed = super().process_event(event)
        if not event_consumed:
            if event.type == TOGGLE_BUTTON:
                fitid = event.user_data["fitid"]
                if self._record['fitid'] == fitid:
                    return False
            elif event.type == budgy.gui.events.CATEGORY_CHANGED:
                if event.fitid == self._record['fitid']:
                    if event.expense_type == BudgyDatabase.RECURRING_EXPENSE_TYPE:
                        self.set_color(self.RECURRING_EXPENSE_COLOR)
                    elif event.expense_type == BudgyDatabase.ONE_TIME_EXPENSE_TYPE:
                        self.set_color(self.ONE_TIME_EXPENSE_COLOR)
                    else:
                        self.set_color(self.NON_EXPENSE_COLOR)
                    return False
        return event_consumed

class RecordViewPanel(UIPanel):
    def __init__(self, database_path:Path, *args, **kwargs):
        if isinstance(database_path, str):
            database_path = Path(database_path)
        if isinstance(database_path, Path):
            database_path = database_path.expanduser()
            self.database = BudgyDatabase(database_path)
        else:
            self.database = database_path
        super().__init__(*args, **kwargs)
        self.record_views = []

        # add the scrollbar
        scrollbar_w = 20

        self.scrollbar = UIVerticalScrollBar(
            pygame.Rect(-scrollbar_w, 0, scrollbar_w, self.relative_rect.height),
            visible_percentage=1.0,
            container=self,
            parent_element=self,
            anchors={
                'top': 'top', 'left': 'right',
                'bottom': 'bottom', 'right': 'right'
            },
        )
        self.visible_records:int = 0
        self.setup_record_views()
        self.last_start_percent = 0

    def setup_record_views(self):
        for rv in self.record_views:
            rv.kill()
        self.record_views:List[RecordView] = []
        # calculate number of visible rows
        h = self.relative_rect.height
        n = math.floor(h / RecordView.RECORD_VIEW_HEIGHT)
        self.visible_records = n
        print(f'We can fit {n} records ({h / RecordView.RECORD_VIEW_HEIGHT})')

        x = 0
        y = 0
        w = self.relative_rect.width - self.scrollbar.relative_rect.width
        h = RecordView.RECORD_VIEW_HEIGHT
        for i in range(n):
            rv = RecordView(
                self.database,
                pygame.Rect(x, y, w, h),
                container=self,
                parent_element=self,
                object_id=ObjectID(object_id='#record-'),
                anchors={
                    'top': 'top', 'left': 'left',
                    'bottom': 'top', 'right': 'right'
                }
            )
            self.record_views.append(rv)
            y += h


    def render_data(self):
        if not self.visible:
            return

        for i in range(self.visible_records):
            if self.starting_row + i < len(self._data):
                self.record_views[i].set_record(self._data[self.starting_row + i])
            else:
                self.record_views[i].set_record(None)

    def set_data(self, rows):
        self._data = rows
        self.starting_row = 0
        self.last_start_percent = self.scrollbar.start_percentage
        n_records = len(self._data)
        pct = self.visible_records / n_records if n_records != 0 else 0
        # do I need to clamp?
        self.scrollbar.set_visible_percentage(pct)
        self.render_data()

    def process_event(self, event: pygame.event.Event) -> bool:
        event_consumed = super().process_event(event)
        if not event_consumed:
            if event.type == pygame.MOUSEWHEEL:
                # Trick the scrollbar into thinking it got the event
                self.scrollbar.scroll_wheel_moved = True
                self.scrollbar.scroll_wheel_amount = event.y
                # forcing an update makes the scrolling smoother
                self.scrollbar.update(0.01)

            if self.scrollbar.has_moved_recently:
                if self.scrollbar.start_percentage != self.last_start_percent:
                    self.last_start_percent = self.scrollbar.start_percentage
                    self.starting_row = math.ceil(len(self._data) * self.last_start_percent)
                    self.render_data()
                    last = min(self.starting_row + self.visible_records, len(self._data))
                    post_show_message(f'Showing Records {self.starting_row} to {last} out of {len(self._data)}')
                event_consumed = True

        return event_consumed
