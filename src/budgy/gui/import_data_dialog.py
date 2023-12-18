import pygame
import pygame_gui
from pygame_gui.windows import UIFileDialog
from pygame_gui.core import ObjectID

import budgy.gui.events
from budgy.gui.configdata import BudgyConfig


class ImportDataDialog(UIFileDialog):
    def __init__(self,
                 config_in:BudgyConfig,
                 rect:pygame.Rect,
                 manager=None):
        self.config = config_in
        super().__init__(rect,
                         manager=manager,
                         window_title='Import Data File',
                         initial_file_path=self.config.import_data_path,
                         object_id=ObjectID(object_id='#import_data_dialog'),
                         allow_existing_files_only=True,
                         allow_picking_directories=False,
                         allowed_suffixes=['.ofx', '.qfx'],
                         visible=True)

    def process_event(self, event: pygame.event.Event):
        if super().process_event(event):
            return True

        return False