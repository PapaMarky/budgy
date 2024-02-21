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

    def set_category_text(self):
        pass