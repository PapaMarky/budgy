import datetime
import math
import re
from typing import List
import pygame

from pygame_gui.core import ObjectID
from pygame_gui.elements import UIPanel, UIVerticalScrollBar, UILabel

import budgy.gui.constants
from budgy.gui.constants import BUTTON_HEIGHT, BUTTON_WIDTH
from budgy.gui.events import post_show_message

class RecordView(UIPanel):
    RECORD_VIEW_HEIGHT = BUTTON_HEIGHT
    field_names = (
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
    field_defs = {
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
            'width': 100,
            'oid': ObjectID(class_id='@record-field', object_id='#field-left')
        }
    }
    def __init__(self,*args, **kwargs):
        kwargs.__setitem__('object_id',
                           ObjectID(class_id='@record-panel'))
        super().__init__(*args, **kwargs)
        self._record:dict = {}
        self._fields:List[UILabel] = []

        x = 0
        for f in self.field_defs:
            w = self.field_defs[f]['width']
            oid = self.field_defs[f]['oid']
            item = UILabel(
                pygame.Rect(x, 0, w, self.RECORD_VIEW_HEIGHT),
                '',
                container=self, parent_element=self,
                object_id=oid,
                anchors={
                    'top': 'top', 'left': 'left',
                    'bottom': 'bottom', 'right': 'left'
                },
            )
            x += w + 1
            self._fields.append(item)
        self.set_record(None)

    def set_record(self, record):
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
                m = re.match(r'^(\d{4}-\d{2}-\d{2})', value)
                if m:
                    value = m.group(1)
                self._fields[i].set_text(str(value))

class RecordViewPanel(UIPanel):
    def __init__(self, *args, **kwargs):
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
        for i in range(self.visible_records):
            if self.starting_row + i < len(self._data):
                self.record_views[i].set_record(self._data[self.starting_row + i])
            else:
                self.record_views[i].set_record(None)

    def set_data(self, rows):
        self._data = rows
        self.starting_row = 0
        self.last_start_percent = self.scrollbar.start_percentage
        pct = self.visible_records / len(self._data)
        # do I need to clamp?
        self.scrollbar.set_visible_percentage(pct)
        self.render_data()

    def process_event(self, event: pygame.event.Event) -> bool:
        if self.scrollbar.has_moved_recently:
            if self.scrollbar.start_percentage != self.last_start_percent:
                print(f'SB: start: {self.scrollbar.start_percentage}')
                self.last_start_percent = self.scrollbar.start_percentage
                self.starting_row = math.ceil(len(self._data) * self.last_start_percent)
                self.render_data()
                post_show_message(f'Showing Records {self.starting_row} to {self.starting_row + self.visible_records} out of {len(self._data)}')