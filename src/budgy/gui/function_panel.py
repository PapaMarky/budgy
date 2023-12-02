import pygame
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIPanel

import budgy
from budgy.gui.configdata import BudgyConfig


class BudgyFunctionPanel(UIPanel):

    def __init__(self, config_in:BudgyConfig, *args, **kwargs):
        self.budgy_config:BudgyConfig = config_in
        super().__init__(*args, **kwargs)
        self._data_panel:UIPanel = self._create_data_panel()
        self._report_panel:UIPanel = self._create_report_panel()
        self.show_subpanel('data')

    class BudgyFunctionSubPanel(UIPanel):
        def __init__(self, config_in: BudgyConfig, function_panel: UIPanel, object_id=''):
            self.budgy_config: BudgyConfig = config_in
            self.parent_panel = function_panel
            x = 0
            y = 0
            w = function_panel.relative_rect.width
            h = function_panel.relative_rect.height
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

    def show_subpanel(self, panel_name):
        print(f'Show function panel: {panel_name}')
        if panel_name == 'data':
            self._data_panel.show()
            self._report_panel.hide()
        elif panel_name == 'report':
            self._data_panel.hide()
            self._report_panel.show()
        else:
            raise Exception(f'show_subpanel: bad panel name: {panel_name}')

    def _create_data_panel(self):
        self._data_panel = self.BudgyFunctionSubPanel(self.budgy_config, self, object_id='#data-panel')
        return self._data_panel

    def _create_report_panel(self):
        self._report_panel = self.BudgyFunctionSubPanel(self.budgy_config, self, object_id='#report-panel')
        return self._report_panel
