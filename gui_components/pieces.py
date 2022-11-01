import os
import pygame

class Piece():
    def __init__(self, name, notation, color, skin_directory="skins/default") -> None:
        self.name = name
        self.notation = notation
        self.color = color
        self.skin_directory = skin_directory

    def get_image_path(self):
        return os.path.join(self.skin_directory, self.color, f"{self.notation}.png")

    def get_image(self):
        image_path = self.get_image_path()

        if os.path.exists(image_path):
            return pygame.image.load(image_path)
        else:
            raise FileNotFoundError(f"The image was not found in the {image_path}")

    def __str__(self):
        return f"{self.notation} {self.color}"

    def get_notation(self) -> str:
        if self.notation != 'p':
            return self.notation.upper()

        return ''

class Pawn(Piece):
    def __init__(self, color, skin_directory) -> None:
        super().__init__("pawn", "", color, skin_directory)

class Knight(Piece):
    def __init__(self, color, skin_directory) -> None:
        super().__init__("knight", "k", color, skin_directory)

class Bishop(Piece):
    def __init__(self, color, skin_directory) -> None:
        super().__init__("bishop", "b", color, skin_directory)

class Rook(Piece):
    def __init__(self, color, skin_directory) -> None:
        super().__init__("rook", "r", color, skin_directory)

class Queen(Piece):
    def __init__(self, color, skin_directory) -> None:
        super().__init__("queen", "q", color, skin_directory)

class King(Piece):
    def __init__(self, color, skin_directory) -> None:
        super().__init__("king", "k", color, skin_directory)