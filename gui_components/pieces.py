import os
import pygame

class Piece:
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
            [-3.0, 0.5, 1.0, 1.5, 1.5, 1.0, 0.5, -3.0],
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

    piece_square_tables = {
        "w": piece_square_tables,
        "b": { key: value[::-1] for key, value in piece_square_tables.items() } # reversing the previous lists
    }

    # negating the values in black's list
    for key, value in piece_square_tables["b"].items():
        piece_square_tables["b"][key] = [ [ -j for j in rank ] for rank in value ]

    def __init__(self, name, notation, color, skin_directory="skins/default", is_captured=False) -> None:
        self.name = name
        self.__notation = notation
        self.color = color
        self.skin_directory = skin_directory
        self.set_is_captured(is_captured)

        self.value = self.get_piece_value()
    
    def get_piece_value(self):
        return Piece.colors_notations_and_values[self.color][self.__notation.lower()]

    def get_piece_color_based_on_notation(notation) -> str:
        return "w" if notation.isupper() else "b"

    def get_value_from_notation(notation: str, color: str) -> int:
        return Piece.colors_notations_and_values[color][notation.lower()]

    def set_is_captured(self, is_captured: bool):
        self.__is_captured = bool(is_captured)

    def get_piece_value_from_notation_and_position(notation: str, color: str, rank_number, file_number):
        position_value = Piece.piece_square_tables[color][notation.lower()][rank_number][file_number]
        
        # negating the value obtained from the piece squares table if the piece is black
        # position_value = -position_value if color == "b" else position_value

        piece_value = Piece.colors_notations_and_values[color][notation.lower()]

        return position_value + piece_value

    def get_image_path(self):
        """
        Gets the path to the image of the piece based on its notation and 
        whether or not it has been captured
        """
        if not self.__is_captured:
            path = os.path.join(self.skin_directory, self.color, f"{self.__notation.lower()}.png")
        else:
            path = os.path.join(self.skin_directory, self.color, "captured", f"{self.__notation.lower()}.png")
        
        return path

    def get_image(self):
        """
        Returns a pygame image object from the piece's corresponding image path
        """
        image_path = self.get_image_path()

        if os.path.exists(image_path):
            return pygame.image.load(image_path)
        else:
            raise FileNotFoundError(f"The image was not found in the {image_path}")

    def __str__(self):
        return f"{self.__notation} {self.color}"

    def get_notation(self) -> str:
        """
        Returns the notation of the piece, (pawns' notations are empty strings)
        """
        if self.__notation != 'p':
            return self.__notation.upper()

        return ''

    def __set_notation(self, notation):
        self.__notation = notation

    def promote(self, notation: str):
        """
        Promotes this piece to a piece with the notation notation.
        It is important to note that promotion does not increase the piece's value, 
        just its capabilities
        """
        if self.__notation.lower() != "p":
            raise ValueError("Cannot promote a piece other than a pawn")
        
        if notation not in ["q", "r", "n", "b"]:
            raise ValueError("Can only promote to queen, rook, bishop or knight pieces")

        self.__set_notation(notation)
        