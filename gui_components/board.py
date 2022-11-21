import chess

import pygame

from gui_components.pieces import Piece

class Square(pygame.Rect):
    def __init__(self, left: float, top: float, width: float, height: float, background_color: str, border_color: str, piece: Piece = None) -> None:
        super().__init__(left, top, width, height)
        self.background_color = background_color
        self.border_color = border_color
        self.piece = piece
        self.is_possible_move = False

    def toggle_is_possible_move(self):
        self.is_possible_move = not self.is_possible_move
        return self
    
    def empty(self):
        self.piece = None

        return self

    def set_is_possible_move(self, value: bool):
        self.is_possible_move = bool(value)
        return self

class ChessSquare(Square):
    def __init__(self, left: float, top: float, width: float, height: float, background_color: str, border_color: str, file_number, rank_number, piece: Piece = None) -> None:
        super().__init__(left, top, width, height, background_color, border_color, piece)
        self.file_number = file_number
        self.rank_number = rank_number
        self.ranks = list( str(i) for i in range(1, 9) )
        self.files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

    def get_chess_square(self) -> chess.Square:
        """
        Returns a chess.Square object that corresponds to this one
        """
        return chess.square(self.file_number, self.rank_number)

    def is_identical_to_chess_square(self, square: chess.Square) -> bool:
        """
        Checks if this object corresponds to a chess.Square object
        """
        return (
            self.file_number == chess.square_file(square) and 
            self.rank_number == chess.square_rank(square)
        )

    def get_rank(self) -> str:
        """
        Gets the rank of the object. Ranks are the rows of the board and they range from 1 to 8
        """
        return self.ranks[ self.rank_number ]

    def get_file(self) -> str:
        """
        Gets the file of the object. Files are the columns of the board and range from A to H
        """
        return self.files[ self.file_number ]

    def get_notation(self) -> str:
        """
        Gets the notation of the square object. A squares notation is simply its file and rank
        """
        return f'{self.get_file()}{self.get_rank()}'

class Board(pygame.sprite.Sprite):
    RANKS = [ i+1 for i in range(0, 8) ]
    FILES = [ chr(i) for i in range(65, 65+9) ]

    def __init__(self, number_of_rows, number_of_columns, left, top, width, height, horizontal_padding, vertical_padding, **kwargs) -> None:
        self.left = left
        self.top = top
        self.number_of_rows = number_of_rows
        self.number_of_columns = number_of_columns
        self.width = width
        self.height = height
        self.horizontal_padding = horizontal_padding
        self.vertical_padding = vertical_padding
        self.squares = []
        
    def create_squares(self):
        pass

class ChessBoard(Board):
    def __init__(
        self, left, top, width, height, 
        horizontal_padding=None, vertical_padding=None, 
        light_square_color: str=(245, 245, 245), dark_square_color: str=(100, 100, 100), 
        previous_square_highlight_color=(186, 202, 43),
        current_square_highlight_color=(246, 246, 105),
        board: chess.Board=None, move_hints=True, **kwargs
    ) -> None:
        super().__init__(
            8, 8, left, top, width, height, 
            horizontal_padding, vertical_padding, **kwargs
        )
        self.__set_square_size()
        self.light_square_color = light_square_color
        self.dark_square_color = dark_square_color
        self.board = board
        self.move_hints = move_hints
        print('The current board is')
        print(self.board)
        self.rect = pygame.Rect(left, top, width, height)

        self.create_squares()
        
        self.captured_pieces = {
            "w": [],
            "b": []
        }
        
        # the square the piece that made the latest move came from
        self.previous_move_square = None 
        self.current_move_square = None 
        
        self.previous_square_highlight_color = previous_square_highlight_color
        self.current_square_highlight_color = current_square_highlight_color

        self.is_flipped = bool(kwargs["flipped"]) if "flipped" in kwargs else False
        
        # set to True if a pawn has the right to promote and has to choose which piece it wants to promote to
        self.awaiting_promotion = False

        # self.flip()
    
    def __set_square_size(self):
        self.__square_size = self.height // 8

    @property
    def square_size(self) -> int:
        return self.__square_size


    def get_piece_from_notation(self, notation):
        """
        Returns a piece object based on a particular notation
        """
        if notation != '.':
            piece_color = "b" if notation.islower() else "w"
            notation = notation.lower()
            piece = Piece(name=notation, notation=notation, color=piece_color)
            
            return piece
        
        return None

    def get_square_from_chess_square(self, square: chess.Square) -> ChessSquare:
        """
        Returns a Square object that corresponds to a particular chess.Square object
        """
        square_file = chess.square_file(square)
        square_rank = chess.square_rank(square)

        rank = self.squares[ 7 - square_rank ]
        
        return rank[ square_file ]

    def create_squares(self):
        """
        Creates the squares oon the board and places pieces on them based on the state of the chess.Board object
        """
        string = self.board.__str__()
        ranks_inverted = string.split('\n')#[::-1]

        for i in range(self.number_of_rows):
            self.squares.append( [] )
            
            rank = ranks_inverted[i].split(' ')

            for j in range(self.number_of_columns):
                square = rank[j]

                piece = self.get_piece_from_notation(square)

                color = self.light_square_color if (i+j) % 2 == 0 else self.dark_square_color

                board_square = ChessSquare( 
                    self.left + (j*self.square_size), self.top + (i*self.square_size), self.square_size, 
                    self.square_size, color, self.dark_square_color, j, 7 - i, piece=piece
                )

                self.squares[i].append( board_square )

    def flip(self):
        """
        Changes the coordinates of the squares in essence flipping them
        """
        board_rect = pygame.Rect(self.left, self.top, self.width, self.height)

        for (i, rank) in enumerate(self.squares):
            print(f"Flipping the squares on rank: {8 - i}")
            for (j, square) in enumerate(rank):
                square: ChessSquare = square
                _old = square.__repr__()

                square.x += (7 - j) * self.square_size
                square.y += (7 - i) * self.square_size
                
                if not square.colliderect(board_rect):
                    print("Square is out of bounds of the board")
                    print(f"The board rectangle is: {board_rect}. The square rectangle is: {square}")

                else:
                    print(f"Square was flipped successfully. Old coordinates: {_old}, new: {square}")

        self.is_flipped = not self.is_flipped

    def place_pieces(self):
        """
        places pieces on the board based on the progress of the board attribute 
        different from create_squares in that it doesn't create squares it instead 
        clears all the squares of existing pieces and positions the pieces on the board
        """
        string = self.board.__str__()
        ranks_inverted = string.split('\n')#[::-1]

        for i in range( self.number_of_rows ):
            rank = ranks_inverted[i].split(' ')

            for j in range( self.number_of_columns ):
                self.squares[i][j].empty()
                board_square = rank[j]

                piece = self.get_piece_from_notation(board_square)

                self.squares[i][j].piece = piece

    def get_possible_moves(self, source_coordinates, remove_hints=False):
        """
        Gets the possible moves from some coordinates and marks the squares as possible moves if move_hints are enabled
        """
        # source_square = [ square.get_chess_square() for square in self.iter_squares() if square.collidepoint(source_coordinates) ]
        source_square = self.get_square_from_coordinates(source_coordinates)

        if source_square:
            destination_chess_squares = [ move.to_square for move in self.board.legal_moves if move.from_square == source_square ]
            destination_squares = [ square.set_is_possible_move(not remove_hints) for square in self.iter_squares() if square.get_chess_square() in destination_chess_squares ]

            return destination_squares
        
        return []

    def get_possible_moves_without_hint(self, source_coordinates):
        """
        Gets the possible moves from some coordinates
        """
        source_square = self.get_square_from_coordinates(source_coordinates)

        if source_square:
            destination_chess_squares = [ move.to_square for move in self.board.legal_moves if move.from_square == source_square ]
            destination_squares = [ square for square in self.iter_squares() if square.get_chess_square() in destination_chess_squares ]

            return destination_squares
        
        return []

    def hide_hints(self):
        """
        Hides the hints on the squares
        """
        [square.set_is_possible_move(False) for square in self.iter_squares()]
    
    def get_square_from_coordinates(self, coordinates, return_chess_square=True) -> ChessSquare:
        """
        Returns a square that corresponds to the coordinates passed
        """
        square = [ (square.get_chess_square() if return_chess_square else square) for square in self.iter_squares() if square.collidepoint(coordinates) ]
        
        if len(square) > 0:
            square = square[0]

            return square
        print(f"There is no square at the {coordinates} coordinates")
        return None

    def get_move_notation(self, source_square: ChessSquare, destination_square: ChessSquare):
        """
        Gets the notation for a particular move made from source_square to destination_square
        """
        move = ''
        
        if source_square.piece:
            other_pieces_of_the_same_type_that_can_make_move = self.get_pieces_that_can_make_move( [source_square.piece.get_notation()], source_square.piece.color, destination_square, [source_square] )
            same_rank = False
            same_file = False

            if source_square.piece.get_notation() != '':
                for square in other_pieces_of_the_same_type_that_can_make_move:
                    if square.rank_number == source_square.rank_number:
                        same_rank = True
                    if square.file_number == source_square.file_number:
                        same_file = True

                move = move + source_square.piece.get_notation()
                
                if same_file or same_rank:
                    if not same_file:
                        move = move + f"{source_square.get_file()}"
                    elif same_file and not same_rank:
                        move = move + f"{source_square.get_rank()}"
                    else:
                        move = move + f"{source_square.get_notation()}"

        if destination_square.piece:
            move = move + 'x'
            
            if source_square.piece and source_square.piece.get_notation() == '':
                move = source_square.get_file() + move


        move = move + f'{destination_square.get_notation()}'

        if source_square.piece.get_notation() == 'K' and source_square.get_file() == 'e' and destination_square.get_file() in [ 'c', 'g' ]:
            # castling
            if destination_square.get_file() == 'c':
                return '0-0-0'
            else:
                return '0-0'

        move = chess.Move(
            from_square=source_square.get_chess_square(), to_square=destination_square.get_chess_square()
        )

        return move

    def get_pieces_that_can_make_move(self, piece_notations: list, color, square: ChessSquare, squares_to_exclude: list):
        """
        Returns the pieces with notations in <piece_notations> list and of color <color> that can make a move the <square> square 
        while excluding the pieces on the <squares_to_exclude> list
        """
        squares_with_pieces_of_specified_types = [ _square for _square in self.iter_squares() if _square.piece and _square.piece.get_notation() in piece_notations and _square.piece.color == color and _square not in squares_to_exclude ]
        squares_that_can_make_move = [ _square for _square in squares_with_pieces_of_specified_types if square in self.get_possible_moves_without_hint(_square.center) ]

        return squares_that_can_make_move

    def play(self, source_coordinates, destination_coordinates):
        """
        Makes a move from source_coordinates to destination_coordinates
        """
        source_square = self.get_square_from_coordinates(source_coordinates, return_chess_square=False)
        destination_square = self.get_square_from_coordinates(destination_coordinates, return_chess_square=False)

        self._play(source_square, destination_square)

    def _play(self, source_square: ChessSquare=None, destination_square: ChessSquare=None, 
        source_chess_square: chess.Square=None, destination_chess_square: chess.Square=None,
        move: chess.Move=None
    ):
        """
        Makes a move based on the arguments.
        """
        if move:
            self.make_move(move)
            self.previous_move_square = self.get_square_from_chess_square(move.from_square)
            self.current_move_square = self.get_square_from_chess_square(move.to_square)

        elif source_square and destination_square:
            move = self.get_move_notation(source_square, destination_square)
            self.make_move(move)
            self.previous_move_square = source_square
            self.current_move_square = destination_square

        elif source_chess_square and destination_chess_square:
            move = chess.Move(from_square=source_chess_square, to_square=destination_chess_square)
            self.make_move(move)
            self.previous_move_square = self.get_square_from_chess_square(source_chess_square)
            self.current_move_square = self.get_square_from_chess_square(destination_chess_square)
        
        else:
            print("None of the conditions were fulfilled. No move is currently being made")
        
        self.place_pieces()

        print('The current board is')
        print(self.board)

    def make_move(self, move):
        """
        Makes a move either with an str object or a chess.Move object
        """
        if isinstance(move, str):
            self.board.push_san(move)
        elif isinstance(move, chess.Move):
            
            if self.board.is_capture(move):
                destination_square: ChessSquare = self.get_square_from_chess_square(move.to_square)
                piece: Piece = destination_square.piece
                
                print("The move was a capture")

                if piece is not None:
                    piece.set_is_captured(True)
                    color = piece.color

                    self.captured_pieces[color].append(piece)

            self.board.push(move)

    def iter_squares(self):
        """
        A generator that returns the different squares on the board
        """
        for rank in self.squares:
            for square in rank:
                yield square

