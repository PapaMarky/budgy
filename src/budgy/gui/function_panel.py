import logging
from pygame_gui.elements import UIPanel

from budgy.core.database import BudgyDatabase
from budgy.gui.configdata import BudgyConfig
from budgy.gui.data_panel import BudgyDataPanel
from budgy.gui.function_subpanel import BudgyFunctionSubPanel
from budgy.gui.report_panel import BudgyReportPanel


class BudgyFunctionPanel(UIPanel):

    def __init__(self, config_in:BudgyConfig, *args, **kwargs):
        self.budgy_config:BudgyConfig = config_in
        super().__init__(*args, **kwargs)
        self._data_panel:BudgyDataPanel = self._create_data_panel()
        self._report_panel:BudgyReportPanel = self._create_report_panel()
        self.show_subpanel('report')

    def set_database(self, database:BudgyDatabase):
        self._report_panel.set_database(database)

    @property
    def data_panel(self) -> BudgyDataPanel:
        return self._data_panel

    @property
    def report_panel(self):
        return self._report_panel

    def show_subpanel(self, panel_name):
        logging.debug(f'Show function panel: {panel_name}')
        if panel_name == 'data':
            self._data_panel.show()
            self._report_panel.hide()
        elif panel_name == 'report':
            self._data_panel.hide()
            self._report_panel.show()
        else:
            raise Exception(f'show_subpanel: bad panel name: {panel_name}')

    def _create_data_panel(self) -> BudgyDataPanel:
        self._data_panel = BudgyDataPanel(self.budgy_config, self, object_id='#data-panel')
        return self._data_panel

    def _create_report_panel(self) -> BudgyReportPanel:
        self._report_panel = BudgyReportPanel(self.budgy_config, self, object_id='#report-panel')
        return self._report_panel

