import pygame
from pygame_gui.elements import UIPanel
from pygame_gui.elements.ui_image import UIImage
from pygame_gui.core.colour_parser import parse_colour_name


class BgColorPanel(UIPanel):

    def __init__(self, color_str:str, *args, **kwargs):
        super().__init__( *args, **kwargs)
        color_surface_size = self.get_container().get_size()
        self.color_image = UIImage(
            pygame.Rect((0, 0), color_surface_size),
            pygame.Surface(color_surface_size).convert(),
            container=self,
            parent_element=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'bottom', 'right': 'right'
            }
        )
        self.set_color(color_str)

    def set_color(self, color_str:str):
        color:pygame.Color = parse_colour_name(color_str)
        self.color_image.image.fill(color)