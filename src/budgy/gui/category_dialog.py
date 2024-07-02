import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIPanel, UIButton

from budgy.core.database import BudgyDatabase
from budgy.gui.category_view_panel import CategoryViewPanel, SubcategoryViewPanel
from budgy.gui.constants import BUTTON_HEIGHT, MARGIN, BUTTON_WIDTH
from budgy.gui.events import CATEGORY_SELECTION_CHANGED, CATEGORY_CHANGED


class CategoryDialog(UIWindow):

    def __init__(self, fitid, database, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fitid = fitid
        self.database:BudgyDatabase = database
        self.top_panel_height = BUTTON_HEIGHT + 5 * MARGIN
        self.panel_width = self.relative_rect.width - 16 * MARGIN # some of the layout bits still mystify me
        self.create_top_panel()
        self.create_middle_panel()
        self.create_bottom_panel()
        self.categories:dict = {}
        self.category = None
        self.subcategory = None
        self.original_category = None
        self.load_categories()
        self.set_blocking(True)

    def create_top_panel(self):
        x = 0
        y = 0
        w = self.panel_width
        h = self.top_panel_height
        rrect = pygame.Rect(x, y, w, h)
        self.top_panel = UIPanel(
            rrect,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'right'
            },
            container=self
        )
        # new, edit, delete buttons
        x = MARGIN
        y = MARGIN
        w = BUTTON_WIDTH
        h = BUTTON_HEIGHT
        self.new_button = UIButton(
            pygame.Rect(x, y, w, h),
            'New Category',
            container=self.top_panel,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'left'
            }
        )
        x += BUTTON_WIDTH + MARGIN
        self.edit_button = UIButton(
            pygame.Rect(x, y, w, h),
            'Edit Category',
            container=self.top_panel,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'left'
            }
        )
        x += BUTTON_WIDTH + MARGIN
        self.delete_button = UIButton(
            pygame.Rect(x, y, w, h),
            'Delete Category',
            container=self.top_panel,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'left'
            }
        )
        x =  - BUTTON_WIDTH - MARGIN
        self.rule_button = UIButton(
            pygame.Rect(x, y, w, h),
            'Create Rule',
            container=self.top_panel,
            anchors={
                'top': 'top', 'left': 'right',
                'bottom': 'top', 'right': 'right'
            }
        )

    def get_selection(self):
        return self.category_panel.selection, self.subcategory_panel.selection

    def set_selection(self, category, subcategory):
        if category != self.category:
            self.category = category
            self.subcategory = subcategory
            self.category_panel.set_selection(category)
            self.subcategory_panel.set_selection(subcategory)

    def create_middle_panel(self):
        x = 0
        y = self.top_panel_height + MARGIN
        w = self.panel_width
        h = self.relative_rect.height - (4 * self.top_panel_height)
        rrect = pygame.Rect(x, y, w, h)
        self.middle_panel = UIPanel(
            rrect,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'bottom', 'right': 'right'
            },
            container=self
        )

        x = MARGIN
        y = MARGIN
        w = (self.middle_panel.relative_rect.width / 2) - MARGIN * 3
        h = self.middle_panel.relative_rect.height - 5 * MARGIN
        rrect = pygame.Rect(x, y, w, h)
        self.category_panel = CategoryViewPanel(
            self.database,
            rrect,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'bottom', 'right': 'right'
            },
            container=self.middle_panel
        )
        x += w + MARGIN
        rrect = pygame.Rect(x, y, w, h)
        self.subcategory_panel = SubcategoryViewPanel(
            self.database,
            rrect,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'bottom', 'right': 'right'
            },
            container=self.middle_panel
        )


    def create_bottom_panel(self):
        x = 0
        y = self.middle_panel.relative_rect.bottom + MARGIN
        w = self.panel_width
        h = self.top_panel_height
        rrect = pygame.Rect(x, y, w, h)
        self.bottom_panel = UIPanel(
            rrect,
            container=self
        )
        # Save, Cancel
        x = MARGIN
        y = MARGIN
        w = BUTTON_WIDTH
        h = BUTTON_HEIGHT
        self.save_button = UIButton(
            pygame.Rect(x, y, w, h),
            'Save',
            container=self.bottom_panel,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'left'
            }
        )
        x += BUTTON_WIDTH + MARGIN
        self.cancel_button = UIButton(
            pygame.Rect(x, y, w, h),
            'Cancel',
            container=self.bottom_panel,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'left'
            }
        )

    def list_categories(self):
        category_list = []
        for cat in self.categories:
            cat_record = {'name': cat}
            if cat == 'No Category':
                category_list.insert(0, cat_record)
            else:
                category_list.append(cat_record)
        # category_list.sort()
        return category_list

    def list_subcategories(self, category):
        if not category in self.categories:
            raise Exception(f'No such category: "{category}"')
        subcategory_list = []
        for subcategory in self.categories[category]:
            subcategory_list.append({'name': subcategory})
        return subcategory_list

    def load_categories(self):
        print(f'Loading Categories (dialog)')
        self.categories = self.database.get_catetory_dict()
        full_category = self.database.get_category_for_fitid(self.fitid)
        category_list = self.list_categories()
        subcategory_list = self.list_subcategories(full_category[0])

        self.category_panel.set_data(category_list)
        self.category_panel.set_selection(full_category[0])

        self.subcategory_panel.set_data(subcategory_list)
        self.subcategory_panel.set_selection(full_category[1])

        self.original_category = full_category

    def save(self):
        category, subcategory = self.get_selection()
        if self.original_category[0] != category or self.original_category[1] != subcategory:
            # TODO: Confirmation Dialog?
            print(f'NEW CATEGORY for {self.fitid}: {category} / {subcategory}')
            self.database.set_txn_category(self.fitid, category, subcategory)
            event_data = {
                'fitid': self.fitid
            }
            pygame.event.post(pygame.event.Event(CATEGORY_CHANGED, event_data))
            self.kill()
        else:
            print(f'CATEGORY UNCHANGED')
    def process_event(self, event: pygame.event.Event) -> bool:
        event_consumed = super().process_event(event)
        if not event_consumed:
            if event.type == CATEGORY_SELECTION_CHANGED:
                if event.is_subcategory:
                    print(f'Subcategory changed to {event.category} (Dialog)')
                    self.subcategory_panel.set_selection(event.category)
                else:
                    print(f'Category changed to {event.category} (Dialog, subcategory: {event.is_subcategory})')
                    self.subcategory_panel.set_data(self.list_subcategories(event.category))
                    self.set_selection(event.category, "")
                return True
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.cancel_button:
                    self.kill()
                    return True
                if event.ui_element == self.save_button:
                    self.save()
        return event_consumed
