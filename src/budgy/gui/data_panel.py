from pathlib import Path

import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIPanel, UIButton

import budgy.gui
from budgy.gui.function_subpanel import BudgyFunctionSubPanel

class BudgyDataPanel(BudgyFunctionSubPanel):
    def __init__(self, config_in, function_panel, *args, **kwargs):
        super().__init__(config_in, function_panel, *args, **kwargs)
        self._import_data_button = UIButton(
            pygame.Rect(0, 0, budgy.gui.BUTTON_WIDTH, budgy.gui.BUTTON_HEIGHT),
            'Import Data',
            self.ui_manager,
            container=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'left'
            }
        )
        x = self._import_data_button.get_relative_rect().right
        y = self._import_data_button.get_relative_rect().top
        w = budgy.gui.BUTTON_WIDTH
        h = self._import_data_button.get_relative_rect().height
        self._clear_data_button = UIButton(
            pygame.Rect(x, y, w, h),
            'Clear Data',
            self.ui_manager,
            container=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'left'
            }
        )

        x = 0
        y = self._clear_data_button.get_relative_rect().bottom + budgy.gui.MARGIN

        w, h = self.get_relative_rect().size
        w -= 6 * budgy.gui.MARGIN
        h -= 6 * budgy.gui.MARGIN + y
        rr = pygame.Rect(x, y, w, h)
        # rr.bottomright = (-budgy.gui.MARGIN, -budgy.gui.MARGIN)
        self._data_view_panel = UIPanel(
            rr,
            manager=self.ui_manager,
            container=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'bottom', 'right': 'right'
            },
            object_id=ObjectID(object_id='#data_view_panel')
        )

    def process_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._import_data_button:
                print('IMPORT DATA')
                return True
            if event.ui_element == self._clear_data_button:
                print('CLEAR DATA')
                return True
        return False