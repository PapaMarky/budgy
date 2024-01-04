import datetime
import math
import re
from typing import List
import pygame

from pygame_gui.core import ObjectID
from pygame_gui.elements import UIPanel, UIVerticalScrollBar, UILabel

import budgy.gui.constants
from budgy.gui.toggle_button import ToggleButton, TOGGLE_BUTTON

from budgy.gui.constants import BUTTON_HEIGHT
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
        'exclude'
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
        'exclude': {
            'position': 4,
            'width': 100,
            'oid': ObjectID(class_id='@record-button', object_id='#field-button')
        }
    }

    def __init__(self,*args, **kwargs):
        kwargs.__setitem__('object_id',
                           ObjectID(class_id='@record-view-panel'))
        super().__init__(*args, **kwargs)
        self._record:dict = {}
        self._outer_record = None
        self._fields:List[UILabel] = []
        layer = 1
        self._highlight = UIPanel(
            pygame.Rect(0,0, self.relative_rect.width, self.relative_rect.height),
            starting_height=layer,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id='@record-highlight'),
            anchors=kwargs.get('anchors')
        )
        layer += 1
        x = 0
        def toggle_callback(state):
            if self.visible:
                self._record['exclude'] = state
                # TODO self._record and self._outer_records should always be in sync. Figure out a way to replace _record
                # with _outer_record so we only have one copy
                if self._outer_record is not None:
                    self._outer_record['exclude'] = state

        self._exclude_button:ToggleButton = None
        for f in self.field_defs:
            w = self.field_defs[f]['width']
            oid = self.field_defs[f]['oid']
            item = None
            if f == 'exclude':
                item = ToggleButton(
                    False,
                    'Excluded',
                    'Included',
                    pygame.Rect(x, 0, w, self.RECORD_VIEW_HEIGHT),
                    'NOT SET',
                    user_data={

                    },
                    callback=toggle_callback,
                    container=self, parent_element=self,
                    object_id=oid,
                    starting_height=layer,
                    anchors={
                        'top': 'top', 'left': 'left',
                        'bottom': 'bottom', 'right': 'left'
                    }
                )
                item.state = False
                item.disable()
                self._exclude_button = item
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
        self.set_record(None)

    def set_record(self, record):
        self._outer_record = record
        if record is None:
            self._exclude_button.disable()
            self._exclude_button.hide()
            self._exclude_button.user_data = None
            self._highlight.visible = False
        else:
            self._exclude_button.enable()
            if self.visible:
                self._exclude_button.show()

        for field in self.field_names:
            if record is None:
                self._record[field] = ''
            else:
                if not field in record:
                    raise Exception(f'Field missing from record: {field}')
                self._record[field] = record[field]
            if field in self.field_defs:
                i = self.field_defs[field]['position']
                value = str(self._record[field]) if field != 'exclude' else self._record[field]
                if field == 'amount' and isinstance(value, float):
                    value = f'{float(value):8.02f}'
                elif field == 'posted':
                    value = value[:10]
                elif field == 'exclude' and value != '':
                    self._fields[i].state = value
                    self._fields[i].user_data = self._record
                    if self.visible:
                        if value:
                            self._highlight.hide()
                        else:
                            self._highlight.show()
                if field != 'exclude':
                    self._fields[i].set_text(str(value))

    def process_event(self, event: pygame.event.Event) -> bool:
        event_consumed = super().process_event(event)
        if not event_consumed:
            if event.type == TOGGLE_BUTTON:
                fitid = event.user_data["fitid"]
                if self._record['fitid'] == fitid:
                    if self._record['exclude']:
                        self._highlight.hide()
                    else:
                        self._highlight.show()
        return event_consumed

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
            if self.scrollbar.has_moved_recently:
                if self.scrollbar.start_percentage != self.last_start_percent:
                    self.last_start_percent = self.scrollbar.start_percentage
                    self.starting_row = math.ceil(len(self._data) * self.last_start_percent)
                    self.render_data()
                    last = min(self.starting_row + self.visible_records, len(self._data))
                    post_show_message(f'Showing Records {self.starting_row} to {last} out of {len(self._data)}')
                event_consumed = True
        return event_consumed
