import datetime
import math
import re
from pathlib import Path
from typing import List
import pygame
from pygame import event as pygame_event

from pygame_gui.core import ObjectID
from pygame_gui.elements import UIPanel, UIVerticalScrollBar, UILabel

from budgy.core.database import BudgyDatabase
from budgy.gui.db_record_view_panel import DbRecordView
from budgy.gui.toggle_button import ToggleButton, TOGGLE_BUTTON

from budgy.gui.constants import BUTTON_HEIGHT
from budgy.gui.events import post_show_message, CATEGORY_SELECTION_CHANGED


class CategoryView(DbRecordView):
    CATEGORY_VIEW_HEIGHT = BUTTON_HEIGHT
    SELECTED_COLOR = 'ivory'
    UNSELECTED_COLOR = 'lightsteelblue'
    EMPTY_COLOR = 'black'
    my_field_names = (
        'name',
    )
    my_field_defs = {
        'name': {
            'position': 0,
            'width': 300,
            'oid': ObjectID(class_id='@record-field', object_id='#field-left')
        }
    }
    def __init__(self, database:BudgyDatabase, is_subcategory:bool, *args, **kwargs):
        kwargs.__setitem__('object_id',
                           ObjectID(class_id='@category-view-panel'))
        self._database = database
        self.is_subcategory = is_subcategory
        super().__init__(database, self.my_field_names, self.my_field_defs, *args, **kwargs)
        self._selected = False

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value
        if self._record is None:
            self.set_color(self.EMPTY_COLOR)
        elif value is None:
            self.set_color(self.EMPTY_COLOR)
        else:
            self.set_color(self.SELECTED_COLOR if value else self.UNSELECTED_COLOR)


    def build_items(self):
        self._record:dict = {}
        self._outer_record = None
        self._fields:List[UILabel] = []
        layer = 1
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
            item = UILabel(
                pygame.Rect(x, 0, w, self.CATEGORY_VIEW_HEIGHT),
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
            self.set_color(self.EMPTY_COLOR)
            self.visible = False
            self._record = None
        else:
            if self._record is None:
                self._record = {}
            self.visible = True

            for field in self.field_names:
                if not field in record:
                    raise Exception(f'Field missing from record: {field}')
                self._record[field] = record[field]

                if field in self.field_defs:
                    i = self.field_defs[field]['position']
                    value = str(self._record[field])
                    if field == 'category':
                        if record is None:
                            self._fields[i].category = None
                        else:
                            self._fields[i].category = self._record['category']
                    if self.is_subcategory and value == '':
                        value = '<No Subcategory>'
                    self._fields[i].set_text(str(value))

    def process_event(self, event: pygame.event.Event) -> bool:
        event_consumed = super().process_event(event)
        if not event_consumed:
            if event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_LEFT:
                scaled_mouse_pos = self.ui_manager.calculate_scaled_mouse_position(event.pos)
                if self.is_enabled and self.drawable_shape.collide_point(scaled_mouse_pos):
                    print(f'Category clicked: {self._record["name"]}')
                    event_data = {
                        'category': self._record['name'],
                        'is_subcategory': self.is_subcategory
                    }
                    pygame_event.post(pygame.event.Event(CATEGORY_SELECTION_CHANGED, event_data))

        return event_consumed

class CategoryViewPanel(UIPanel):
    def __init__(self, database_path:Path, *args, **kwargs):
        if isinstance(database_path, str):
            database_path = Path(database_path)
        if isinstance(database_path, Path):
            database_path = database_path.expanduser()
            self.database = BudgyDatabase(database_path)
        else:
            self.database = database_path
        super().__init__(*args, **kwargs)
        self.category_views = []

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
        self.setup_category_views()
        self.last_start_percent = 0
        self._selection = None

        self.starting_row = 0
        self._data = None

    @property
    def is_subcategory(self):
        return False

    @property
    def selection(self):
        return self._selection

    def set_selection(self, category):
        print(f'Set selection (panel): {category}')
        self._selection = category
        self.render_data()

    def setup_category_views(self):
        for rv in self.category_views:
            rv.kill()
        self.category_views:List[CategoryView] = []
        # calculate number of visible rows
        h = self.relative_rect.height
        n = math.floor(h / CategoryView.CATEGORY_VIEW_HEIGHT)
        self.visible_records = n
        print(f'We can fit {n} records ({h / CategoryView.CATEGORY_VIEW_HEIGHT})')

        x = 0
        y = 0
        w = self.relative_rect.width - self.scrollbar.relative_rect.width
        h = CategoryView.CATEGORY_VIEW_HEIGHT
        for i in range(n):
            rv = CategoryView(
                self.database,
                self.is_subcategory,
                pygame.Rect(x, y, w, h),
                container=self,
                parent_element=self,
                object_id=ObjectID(object_id='#category-'),
                anchors={
                    'top': 'top', 'left': 'left',
                    'bottom': 'top', 'right': 'right'
                }
            )
            self.category_views.append(rv)
            y += h


    def render_data(self):
        if not self.visible or self._data is None:
            pass

        for i in range(self.visible_records):
            if self.starting_row + i < len(self._data):
                if self.is_subcategory:
                    pass
                self.category_views[i].set_record(self._data[self.starting_row + i])
                self.category_views[i].selected = (self._selection == self._data[self.starting_row + i]['name'])
            else:
                self.category_views[i].set_record(None)
                self.category_views[i].selected = False

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

            if False and event.type == CATEGORY_SELECTION_CHANGED:
                print(f'Category changed to {event.category}')
                self.set_selection(event.category)
                self.render_data()
        return event_consumed

class SubcategoryViewPanel(CategoryViewPanel):
    def __init__(self, database_path:Path, *args, **kwargs):
        super().__init__(database_path, *args, **kwargs)

    @property
    def is_subcategory(self):
        return True

    def process_event(self, event: pygame.event.Event) -> bool:
        event_consumed = super().process_event(event)
        if not event_consumed:

            if False and event.type == CATEGORY_SELECTION_CHANGED:
                print(f'Category changed to {event.category}')
                self.set_selection(event.category)
                self.render_data()
        return event_consumed
