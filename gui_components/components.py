import pygame

class BorderedRectangle():
    def __init__(
        self, left: float, top: float, width: float, height: float, 
        background_color: str, border_color: str, border_width: int
    ) -> None:
        self.background_color = background_color
        self.border_color = border_color
        self.is_possible_move = False

        self.outer_rectangle = pygame.Rect(left, top, width, height)
        
        self.inner_rectangle = pygame.Rect(
            left+(border_width / 2), top+(border_width/2), 
            width - border_width, height - border_width
        )