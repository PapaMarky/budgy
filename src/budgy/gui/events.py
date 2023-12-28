
from pygame import event as pygame_event

OPEN_DATABASE = pygame_event.custom_type()
DATA_SOURCE_SELECTED = pygame_event.custom_type()
DATA_SOURCE_CONFIRMED = pygame_event.custom_type()
DELETE_ALL_DATA = pygame_event.custom_type()
DELETE_ALL_DATA_CONFIRMED = pygame_event.custom_type()
SELECT_DATABASE = pygame_event.custom_type()
SELECT_SOURCE_FILE = pygame_event.custom_type()


SHOW_MESSAGE = pygame_event.custom_type()
CLEAR_MESSAGES = pygame_event.custom_type()
SHOW_PROGRESS = pygame_event.custom_type()
HIDE_PROGRESS = pygame_event.custom_type()

def post_show_message(message, level='info'):
    event_data = {
        'message': message,
        'level': level
    }
    pygame_event.post(pygame_event.Event(SHOW_MESSAGE, event_data))

def post_clear_messages():
    pygame_event.post(pygame_event.Event(CLEAR_MESSAGES))

def post_show_progress(value, total):
    event_data = {
        'value': value,
        'total': total
    }
    pygame_event.post(pygame_event.Event(SHOW_PROGRESS, event_data))

def post_hide_progress():
    pygame_event.post(pygame_event.Event(HIDE_PROGRESS))