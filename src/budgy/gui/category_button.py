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
        super().__init__(*args, **kwargs)

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
                pygame.Rect(20, 20, 800, 600),
                self.ui_manager,
                'Choose Category'
            )
            return True

    def set_category_text(self):
        category = self.database.get_category_for_fitid(self.fitid)
        expense_marker = '*' if category[2] != 0 else ''
        category_str = f'{expense_marker}{category[0]}' if category[1] == '' else f'{expense_marker}{category[0]} | {category[1]}'
        self.set_text(category_str)
