import pygame
from pygame_gui.elements import UILabel, UIPanel, UIProgressBar
from pygame_gui.core import ObjectID

# Layout constants
TEXT_WIDTH = 175
event_consumed = True

class GeneratedMessagePanel(UIPanel):
    """
    Generated from ../src/budgy/gui/message_panel.py
    """

    def __init__(self, *args, **kwargs):
        """Initialize GeneratedMessagePanel"""
        super().__init__(*args, **kwargs)

        # Create UIPanel
        self._MessagePanel = UIPanel(
            pygame.Rect(0, 0, 100, 100),
            manager=self.ui_manager,
            anchors={'top': 'top', 'left': 'left', 'bottom': 'bottom', 'right': 'right'}
        )

        # Create UIProgressBar
        self._progress_bar = UIProgressBar(
            pygame.Rect(0, 0, 0, 0),
            manager=self.ui_manager,
            container=self.MessagePanel,
            anchors={'top': 'top', 'left': 'left', 'bottom': 'top', 'right': 'right'}
        )

        # Create UILabel: "Message Element"
        self._message_element = UILabel(
            pygame.Rect(0, 0, 0, 0),
            "Message Element",
            manager=self.ui_manager,
            container=self.MessagePanel,
            anchors={'top': 'top', 'left': 'left', 'bottom': 'top', 'right': 'right'},
            object_id=ObjectID(class_id="#message-info @bold-16")
        )

        # Create UILabel: "Message Element"
        self._message_error = UILabel(
            pygame.Rect(0, 0, 0, 0),
            "Message Element",
            manager=self.ui_manager,
            container=self.MessagePanel,
            anchors={'top': 'top', 'left': 'left', 'bottom': 'top', 'right': 'right'},
            object_id=ObjectID(class_id="#message-error @bold-16")
        )

    @property
    def MessagePanel(self):
        """Access the UIPanel component"""
        return self._MessagePanel

    @property
    def progress_bar(self):
        """Access the UIProgressBar component"""
        return self._progress_bar

    @property
    def message_element(self):
        """Access the UILabel component"""
        return self._message_element

    @property
    def message_error(self):
        """Access the UILabel component"""
        return self._message_error
