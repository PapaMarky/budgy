from pygame_gui.elements import UIPanel

from budgy.gui.configdata import BudgyConfig
from budgy.gui.data_panel import BudgyDataPanel
from budgy.gui.function_subpanel import BudgyFunctionSubPanel

class BudgyFunctionPanel(UIPanel):

    def __init__(self, config_in:BudgyConfig, *args, **kwargs):
        self.budgy_config:BudgyConfig = config_in
        super().__init__(*args, **kwargs)
        self._data_panel:UIPanel = self._create_data_panel()
        self._report_panel:UIPanel = self._create_report_panel()
        self.show_subpanel('data')

    @property
    def data_panel(self) -> BudgyDataPanel:
        return self._data_panel

    @property
    def report_panel(self):
        return self._report_panel

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
        self._data_panel = BudgyDataPanel(self.budgy_config, self, object_id='#data-panel')
        return self._data_panel

    def _create_report_panel(self):
        self._report_panel = BudgyFunctionSubPanel(self.budgy_config, self, object_id='#report-panel')
        return self._report_panel

