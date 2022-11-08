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
        return chess.square(self.file_number, self.rank_number)

    def is_identical_to_chess_square(self, square: chess.Square) -> bool:
        return (
            self.file_number == chess.square_file(square) and 
            self.rank_number == chess.square_rank(square)
        )

    def get_rank(self) -> str:
        return self.ranks[ self.rank_number ]

    def get_file(self) -> str:
        return self.files[ self.file_number ]

    def get_notation(self) -> str:
        return f'{self.get_file()}{self.get_rank()}'

class Board(pygame.sprite.Sprite):
    def __init__(self, number_of_rows, number_of_columns, left, top, width, height, horizontal_padding, vertical_padding) -> None:
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
        horizontal_padding, vertical_padding, 
        light_square_color: str=(245, 245, 245), dark_square_color: str=(100, 100, 100), 
        previous_square_highlight_color=(223, 227, 67),
        square_size=64, board=None, move_hints=True
    ) -> None:
        super().__init__(
            8, 8, left, top, width, height, 
            horizontal_padding, vertical_padding
        )
        self.square_size = square_size
        self.light_square_color = light_square_color
        self.dark_square_color = dark_square_color
        self.board = board
        self.move_hints = move_hints
        print('The current board is')
        print(self.board)

        self.create_squares()
        
        # the square the piece that made the latest move came from
        self.previous_move_square = None 
        self.previous_square_highlight_color = previous_square_highlight_color
    
    def get_piece_from_notation(self, notation):
        if notation != '.':
            piece_color = "b" if notation.islower() else "w"
            notation = notation.lower()
            piece = Piece(name=notation, notation=notation, color=piece_color)
            
            return piece
        
        return None

    def get_square_from_chess_square(self, square: chess.Square) -> ChessSquare:
        square_file = chess.square_file(square)
        square_rank = chess.square_rank(square)

        rank = self.squares[ 7 - square_rank ]
        
        return rank[ square_file ]

    def create_squares(self):
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
        # source_square = [ square.get_chess_square() for square in self.iter_squares() if square.collidepoint(source_coordinates) ]
        source_square = self.get_square_from_coordinates(source_coordinates)

        if source_square:
            destination_chess_squares = [ move.to_square for move in self.board.legal_moves if move.from_square == source_square ]
            destination_squares = [ square.set_is_possible_move(not remove_hints) for square in self.iter_squares() if square.get_chess_square() in destination_chess_squares ]

            return destination_squares
        
        return []

    def get_possible_moves_without_hint(self, source_coordinates):
        source_square = self.get_square_from_coordinates(source_coordinates)

        if source_square:
            destination_chess_squares = [ move.to_square for move in self.board.legal_moves if move.from_square == source_square ]
            destination_squares = [ square for square in self.iter_squares() if square.get_chess_square() in destination_chess_squares ]

            return destination_squares
        
        return []

    def hide_hints(self):
        [square.set_is_possible_move(False) for square in self.iter_squares()]
    
    def get_square_from_coordinates(self, coordinates, return_chess_square=True) -> ChessSquare:
        square = [ (square.get_chess_square() if return_chess_square else square) for square in self.iter_squares() if square.collidepoint(coordinates) ]
        
        if len(square) > 0:
            square = square[0]

            return square
        print(f"There is no square at the {coordinates} coordinates")
        return None

    def get_move_notation(self, source_square: ChessSquare, destination_square: ChessSquare):
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
        squares_with_pieces_of_specified_types = [ _square for _square in self.iter_squares() if _square.piece and _square.piece.get_notation() in piece_notations and _square.piece.color == color and _square not in squares_to_exclude ]
        squares_that_can_make_move = [ _square for _square in squares_with_pieces_of_specified_types if square in self.get_possible_moves_without_hint(_square.center) ]

        return squares_that_can_make_move

    def play(self, source_coordinates, destination_coordinates):
        source_square = self.get_square_from_coordinates(source_coordinates, return_chess_square=False)
        destination_square = self.get_square_from_coordinates(destination_coordinates, return_chess_square=False)

        print(f"Making a move. The source square is {source_square.get_notation()}, the destination square is {destination_square.get_notation()}")
        print(f"The piece on the source square is: {source_square.piece.__str__()}")

        self._play(source_square, destination_square)

    def _play(self, source_square: ChessSquare=None, destination_square: ChessSquare=None, 
        source_chess_square: chess.Square=None, destination_chess_square: chess.Square=None,
        move: chess.Move=None
    ):
        if move:
            self.make_move(move)
            self.previous_move_square = self.get_square_from_chess_square(move.from_square)

        elif source_square and destination_square:
            move = self.get_move_notation(source_square, destination_square)
            self.make_move(move)
            self.previous_move_square = source_square

        elif source_chess_square and destination_chess_square:
            move = chess.Move(from_square=source_chess_square, to_square=destination_chess_square)
            self.make_move(move)
            self.previous_move_square = self.get_square_from_chess_square(source_chess_square)
        
        else:
            print("None of the conditions were fulfilled. No move is currently being made")
        
        self.place_pieces()

        print('The current board is')
        print(self.board)

    def make_move(self, move):
        if isinstance(move, str):
            self.board.push_san(move)
        elif isinstance(move, chess.Move):
            self.board.push(move)

    def iter_squares(self):
        for rank in self.squares:
            for square in rank:
                yield square