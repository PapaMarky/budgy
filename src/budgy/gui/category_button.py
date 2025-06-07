import pygame
import pygame_gui
from pygame_gui.elements import UIButton

from budgy.core.database import BudgyDatabase
from budgy.gui.category_dialog import CategoryDialog

class CategoryButton(UIButton):
    def __init__(self,
                 database:BudgyDatabase,
                 *args,
                 fitid = None,
                 category = BudgyDatabase.DEFAULT_CATEGORY,
                 **kwargs
                 ):
        self.category = category
        self.database = database
        self._fitid = fitid
        self._txn_name = 'None'
        self.expense_type = BudgyDatabase.NON_EXPENSE_TYPE
        super().__init__(*args, **kwargs)

    @property
    def txn_name(self):
        return self._txn_name

    @txn_name.setter
    def txn_name(self, txn_name):
        self._txn_name = txn_name

    @property
    def fitid(self):
        return self._fitid

    @fitid.setter
    def fitid(self, fitid):
        self._fitid = fitid
        self.set_category_text()

    def process_event(self, event: pygame.event.Event) -> bool:
        if super().process_event(event):
            return True
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self:
            print(f'Category Button pressed for {self.fitid}')
            self.dialog = CategoryDialog(
                self.fitid,
                self.database,
                pygame.Rect(20, 20, 800, 800),
                self.ui_manager,
                f'Choose Category for "{self.txn_name}"'
            )
            return True

    def set_category_text(self):
        category = self.database.get_category_for_fitid(self.fitid)
        self.expense_type = category[2]
        expense_marker = '*' if self.expense_type != BudgyDatabase.NON_EXPENSE_TYPE else ''
        category_str = f'({category[2]}) {category[0]}' if category[1] == '' else f'({category[2]}) {category[0]} | {category[1]}'
        self.set_text(category_str)
