from abc import ABC, abstractmethod

from pygame_gui.core import ObjectID
from pygame_gui.elements import UILabel

from budgy.core.database import BudgyDatabase
from budgy.gui.constants import BUTTON_HEIGHT
from budgy.gui.bg_color_panel import BgColorPanel
from typing import List


class DbRecordView(BgColorPanel):
    RECORD_VIEW_HEIGHT = BUTTON_HEIGHT
    def __init__(self, database:BudgyDatabase, fields_names, field_defs, *args, **kwargs):
        kwargs.__setitem__('object_id',
                           ObjectID(class_id='@record-view-panel'))
        self.field_names = fields_names
        self.field_defs = field_defs
        self._database = database
        super().__init__('Ivory', *args, **kwargs)
        self._record:dict = {}
        self._fields:List[UILabel] = []
        self.build_items()
        self.set_record(None)

    def build_items(self):
        raise Exception('Call to unimplemented function build_items()')
