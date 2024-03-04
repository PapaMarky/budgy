import pygame
import pygame_gui
from pygame_gui.elements import UIButton

from budgy.core.database import BudgyDatabase


class CategoryButton(UIButton):
    def __init__(self,
                 database:BudgyDatabase,
                 *args,
                 fitid = None,
                 category = 1,
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
            return True

    def set_category_text(self):
        category = self.database.get_category_text_for_fitid(self.fitid)
        self.set_text(category['name'])