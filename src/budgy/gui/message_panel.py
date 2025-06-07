import pygame
from pygame_gui.elements import UIPanel, UIProgressBar, UILabel
from pygame_gui.core import ObjectID
from budgy.gui.constants import MARGIN, BUTTON_HEIGHT
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

        y = MARGIN
        progress_width = self.relative_rect.width * 0.9
        x = self.relative_rect.width / 2 - progress_width / 2
        self.progress_bar = UIProgressBar(
            pygame.Rect(x, y, progress_width, BUTTON_HEIGHT),
            manager=self.ui_manager,
            container=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'right'
            },
            visible=False
        )

        y += MARGIN + BUTTON_HEIGHT
        self.message_element = UILabel(
            pygame.Rect(MARGIN, y, self.relative_rect.width, BUTTON_HEIGHT),
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

        # y += MARGIN + BUTTON_HEIGHT
        self.message_error = UILabel(
            pygame.Rect(MARGIN, y, self.relative_rect.width, BUTTON_HEIGHT),
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
        event_consumed = super().process_event(event)
        if not event_consumed:
            if event.type == SHOW_MESSAGE:
                print(f'SHOW_MESSAGE ({event.level}) {event.message}')
                if event.level in self.level_map:
                    self.level_map[event.level](event.message)
                else:
                    self.error(f'BAD MESSAGE LEVEL: {event.level} ({event.message})')
                event_consumed = True
            elif event.type == CLEAR_MESSAGES:
                self.hide_all_messages()
                event_consumed = True
        return event_consumed