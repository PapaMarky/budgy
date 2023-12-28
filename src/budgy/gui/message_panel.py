import pygame
from pygame_gui.elements import UIPanel, UIProgressBar, UILabel
from pygame_gui.core import ObjectID
from budgy.gui.events import SHOW_MESSAGE, CLEAR_MESSAGES
import budgy


class MessagePanel(UIPanel):
    TEXT_WIDTH = 175
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.level_map = {
            'info': self.info,
            'error': self.error
        }

        y = budgy.gui.MARGIN
        progress_width = self.relative_rect.width * 0.9
        x = self.relative_rect.width / 2 - progress_width / 2
        self.progress_bar = UIProgressBar(
            pygame.Rect(x, y, progress_width, budgy.gui.BUTTON_HEIGHT),
            manager=self.ui_manager,
            container=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'right'
            },
            visible=False
        )

        y += budgy.gui.MARGIN + budgy.gui.BUTTON_HEIGHT
        self.message_element = UILabel(
            pygame.Rect(budgy.gui.MARGIN, y, self.relative_rect.width, budgy.gui.BUTTON_HEIGHT),
            'Message Element',
            manager=self.ui_manager,
            container=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'right'
            },
            object_id=ObjectID(class_id='#message-info', object_id='@bold-16'),
            visible=False
        )

        # y += budgy.gui.MARGIN + budgy.gui.BUTTON_HEIGHT
        self.message_error = UILabel(
            pygame.Rect(budgy.gui.MARGIN, y, self.relative_rect.width, budgy.gui.BUTTON_HEIGHT),
            'Message Element',
            manager=self.ui_manager,
            container=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'right'
            },
            object_id=ObjectID(class_id='#message-error', object_id='@bold-16'),
            visible=False
        )

    def hide_all_messages(self):
        self.message_element.hide()
        self.message_error.hide()

    def error(self, message):
        self.hide_all_messages()
        self.message_error.set_text(message)
        self.message_error.show()

    def info(self, message):
        self.hide_all_messages()
        self.message_element.set_text(message)
        self.message_element.show()

    def process_event(self, event: pygame.event.Event) -> bool:
        if event.type == SHOW_MESSAGE:
            if event.level in self.level_map:
                self.level_map[event.level](event.message)
            else:
                self.error(f'BAD MESSAGE LEVEL: {event.level} ({event.message})')
        elif event.type == CLEAR_MESSAGES:
            self.hide_all_messages()