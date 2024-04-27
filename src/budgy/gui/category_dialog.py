import pygame
from pygame_gui.elements import UIWindow, UIPanel, UIButton

from budgy.gui.constants import BUTTON_HEIGHT, MARGIN, BUTTON_WIDTH


class CategoryDialog(UIWindow):

    def __init__(self, fitid, database, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fitid = fitid
        self.database = database
        self.top_panel_height = BUTTON_HEIGHT + 5 * MARGIN
        self.panel_width = self.relative_rect.width - 16 * MARGIN # some of the layout bits still mystify me
        self.create_top_panel()
        self.create_middle_panel()
        self.create_bottom_panel()

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
        self.category_panel = UIPanel(
            rrect,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'bottom', 'right': 'right'
            },
            container=self.middle_panel
        )
        x += w + MARGIN
        rrect = pygame.Rect(x, y, w, h)
        self.subcategory_panel = UIPanel(
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
