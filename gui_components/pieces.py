import numpy
import os
import pygame

colors_notations_and_values = {
    "w": {
        "p": 1,
        "n": 3,
        "b": 3,
        "r": 5,
        "q": 9,
        "k": 90
    }, 
    "b": {
        "p": -1,
        "n": -3,
        "b": -3,
        "r": -5,
        "q": -9,
        "k": -90
    }
}

piece_square_tables = {
    "k": [
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
        [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
        [2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0],
        [2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 3.0, 2.0]
    ],
    "q": [
        [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
        [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
        [-1.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
        [-0.5, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
        [0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
        [-1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
        [-1.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, -1.0],
        [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]
    ],
    "r": [
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],
        [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
        [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
        [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
        [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
        [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
        [0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0]
    ],
    "b": [
        [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
        [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
        [-1.0, 0.0, 0.5, 1.0, 1.0, 1.0, 0.5, 0.0, -1.0],
        [-1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, -1.0],
        [-1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0],
        [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0],
        [-1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, -1.0],
        [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]
    ],
    "n": [
        [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
        [-4.0, -2.0, 0.0, 0.0, 0.0, 0.0, -2.0, -4.0],
        [-3.0, 0.0, 1.0, 1.5, 1.5, 1.0, 0.0, -3.0],
        [-3.0, 0.5, 1.5, 2.0, 2.0, 1.5, 0.5, -3.0],
        [-3.0, 0.0, 1.5, 2.0, 2.0, 1.5, 0.0, -3.0],
        [-3.0, 0.5, 1.0, 1.5, 1.5, 1.0, 0.5, 3.0],
        [-4.0, -2.0, 0.0, 0.5, 0.5, 0.0, -2.0, -4.0],
        [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]
    ],
    "p": [
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
        [1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0],
        [0.5, 0.5, 1.0, 2.5, 2.5, 1.0, 0.5, 0.5],
        [0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0],
        [0.5, -0.5, -1.0, 0.0, 0.0, -1.0, -0.5, 0.5],
        [0.5, 1.0, 1.0, -2.0, -2.0, 1.0, 1.0, 0.5],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ]
}

class Piece():
    def __init__(self, name, notation, color, skin_directory="skins/default", value: int=None) -> None:
        self.name = name
        self.__notation = notation
        self.color = color
        self.skin_directory = skin_directory

        if value:
            self.value = value if self.color == "w" else value * -1
        else:
            self.value = self.get_piece_value()
    
    def get_piece_value(self):
        return colors_notations_and_values[self.color][self.__notation.lower()]

    def get_piece_color_based_on_notation(notation) -> str:
        return "w" if notation.isupper() else "b"

    def get_value_from_notation(notation: str, color: str) -> int:
        return colors_notations_and_values[color][notation.lower()]

    def get_piece_value_from_notation_and_position(notation: str, color: str, rank_number, file_number):
        position_value = piece_square_tables[notation.lower()][7 - rank_number][7 - file_number]
        
        # negating the value obtained from the piece squares table if the piece is black
        position_value = -position_value if color == "b" else position_value

        piece_value = colors_notations_and_values[color][notation.lower()]

        return position_value + piece_value

    def get_image_path(self):
        return os.path.join(self.skin_directory, self.color, f"{self.__notation.lower()}.png")

    def get_image(self):
        image_path = self.get_image_path()

        if os.path.exists(image_path):
            return pygame.image.load(image_path)
        else:
            raise FileNotFoundError(f"The image was not found in the {image_path}")

    def __str__(self):
        return f"{self.__notation} {self.color}"

    def get_notation(self) -> str:
        if self.__notation != 'p':
            return self.__notation.upper()

        return ''

    def __set_notation(self, notation):
        self.__notation = notation

    def promote(self, notation: str):
        """
        Promotes this piece to a piece with the notation
        """
        if self.__notation.lower() != "p":
            raise ValueError("Cannot promote a piece other than a pawn")
        
        if notation not in ["q", "r", "n", "b"]:
            raise ValueError("Can only promote to queen, rook, bishop or knight pieces")

        self.__set_notation(notation)
        

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