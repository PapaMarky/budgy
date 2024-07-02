import pygame.event

OPEN_DATABASE = pygame.event.custom_type()
DATA_SOURCE_SELECTED = pygame.event.custom_type()
DATA_SOURCE_CONFIRMED = pygame.event.custom_type()
DELETE_ALL_DATA = pygame.event.custom_type()
DELETE_ALL_DATA_CONFIRMED = pygame.event.custom_type()
SELECT_DATABASE = pygame.event.custom_type()
SELECT_SOURCE_FILE = pygame.event.custom_type()
CATEGORY_SELECTION_CHANGED = pygame.event.custom_type()
CATEGORY_CHANGED = pygame.event.custom_type()


SHOW_MESSAGE = pygame.event.custom_type()
CLEAR_MESSAGES = pygame.event.custom_type()
SHOW_PROGRESS = pygame.event.custom_type()
HIDE_PROGRESS = pygame.event.custom_type()

TOGGLE_BUTTON = pygame.event.custom_type()

def post_show_message(message, level='info'):
    event_data = {
        'message': message,
        'level': level
    }
    pygame.event.post(pygame.event.Event(SHOW_MESSAGE, event_data))

def post_clear_messages():
    pygame.event.post(pygame.event.Event(CLEAR_MESSAGES))

def post_show_progress(value, total):
    event_data = {
        'value': value,
        'total': total
    }
    pygame.event.post(pygame.event.Event(SHOW_PROGRESS, event_data))

def post_hide_progress():
    pygame.event.post(pygame.event.Event(HIDE_PROGRESS))