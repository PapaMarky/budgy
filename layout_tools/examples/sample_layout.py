import pygame
from pygame_gui.elements import UIDropDownMenu, UILabel, UIPanel
from pygame_gui.core import ObjectID

# Layout constants
BUTTON_HEIGHT = 25
MARGIN = 2

class SampleTopPanel(UIPanel):
    """
    Generated from JSON layout
    """

    LABEL_WIDTH = 175
    DROPDOWN_WIDTH = 200
    BUTTON_HEIGHT = 25

    def __init__(self, *args, **kwargs):
        """Initialize SampleTopPanel"""
        super().__init__(*args, **kwargs)

        # Create UIPanel
        self.panel = UIPanel(
            pygame.Rect(0, 0, 1280, 100),
            manager=self.ui_manager,
            anchors={'top': 'top', 'left': 'left', 'bottom': 'top', 'right': 'right'},
            object_id=ObjectID(class_id="#top-panel")
        )

        # Create UIDropDownMenu: "Report Functions"
        self.dropdown = UIDropDownMenu(
            pygame.Rect(-202, 2, 200, 25),
            "Report Functions",
            manager=self.ui_manager,
            container=self.panel,
            anchors={'top': 'top', 'left': 'right', 'bottom': 'top', 'right': 'right'},
            object_id=ObjectID(class_id="#dropdown")
        )

        # Create UILabel: "Record Count:"
        self.label = UILabel(
            pygame.Rect(2, 2, 175, 25),
            "Record Count:",
            manager=self.ui_manager,
            container=self.panel,
            object_id=ObjectID(class_id="#data-label")
        )

        # Create UILabel: "No Database"
        self.value = UILabel(
            pygame.Rect(179, 2, 1099, 25),
            "No Database",
            manager=self.ui_manager,
            container=self.panel,
            anchors={'top': 'top', 'left': 'left', 'bottom': 'top', 'right': 'right'},
            object_id=ObjectID(class_id="#data-text")
        )

    @property
    def panel(self):
        """Access the UIPanel component"""
        return self.panel

    @property
    def label(self):
        """Access the UILabel component"""
        return self.label

    @property
    def value(self):
        """Access the UILabel component"""
        return self.value

    @property
    def dropdown(self):
        """Access the UIDropDownMenu component"""
        return self.dropdown
