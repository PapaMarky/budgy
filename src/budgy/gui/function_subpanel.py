import budgy.gui
import pygame
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIPanel

from budgy.gui.configdata import BudgyConfig
from budgy.gui.constants import MARGIN


class BudgyFunctionSubPanel(UIPanel):
    def __init__(self, config_in: BudgyConfig, function_panel: UIPanel, object_id=''):
        self.budgy_config: BudgyConfig = config_in
        self.parent_panel = function_panel
        x = MARGIN
        y = MARGIN
        w = function_panel.relative_rect.width - (4 * MARGIN)
        h = function_panel.relative_rect.height - (4 * MARGIN)
        subpanel_rect: pygame.Rect = pygame.Rect(x, y, w, h)
        super().__init__(
            subpanel_rect,
            starting_height=1,
            manager=function_panel.ui_manager,
            container=function_panel,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'bottom', 'right': 'right'
            },
            object_id=ObjectID(class_id='@function_subpanel', object_id=object_id)
        )
