import logging
import pygame
from pygame import event as pygame_event

import pygame_gui
from pygame_gui.elements import UIButton
from budgy.gui.events import TOGGLE_BUTTON

class ToggleButton(UIButton):
    def __init__(self,
                 initial_state:bool,
                 true_string:str,
                 false_string:str,
                 *args,
                 user_data = None,
                 callback = None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self._state = initial_state
        self._true_string = true_string
        self._false_string = false_string
        self._user_data = user_data
        self.state = self._state
        self.callback = callback

    @property
    def user_data(self):
        return self._user_data

    @user_data.setter
    def user_data(self, new_data):
        self._user_data = new_data

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        changed = self._state != new_state
        self._state = new_state
        if self._state:
            self.set_text(self._true_string)
        else:
            self.set_text(self._false_string)
        if changed and self.callback:
            self.callback(self._state)

    def process_event(self, event: pygame.event.Event) -> bool:
        event_consumed = super().process_event(event)
        if not event_consumed:
            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self:
                self.state = not self.state
                event_consumed = True
                event_data = {
                    'user_data': self.user_data,
                    'state': self.state
                }
                pygame_event.post(pygame.event.Event(TOGGLE_BUTTON, event_data))
                logging.debug(f'Post TOGGLE_BUTTON ({TOGGLE_BUTTON})')

        return event_consumed

