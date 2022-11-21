import threading
from xml.dom import ValidationErr
import chess

from ai import players as ai_players
from gui_components.board import ChessBoard
import pygame

from gui_components.pieces import Piece

BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (255, 255, 255)

pygame.mixer.init()

from gui_components.components import BorderedRectangle

class ChessGame:
    BOARD_DIMENSIONS = (400, 400)
    BOARD_OUTERMOST_BORDER_DIMENSIONS = (500, 500)

    COLORS = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "default": {
            "dark": (100, 100, 100),
            "light": (245, 245, 245)
        },
        "move_highlight": (50, 50, 50)
    }

    SOUNDS = {
        "checkmate": pygame.mixer.Sound("sound_effects/checkmate.mp3"),
        "check": pygame.mixer.Sound("sound_effects/check.mp3"),
        "move": pygame.mixer.Sound("sound_effects/piece_move.mp3")
    }

    def __init__(
        self, screen: pygame.Surface, players: dict, 
        show_ranks_and_files=True, show_captured_pieces=True, screen_width=500, screen_height=500, 
        origin: tuple=None, board=None
    ) -> None:
        self.players = players
        self.show_ranks_and_files = show_ranks_and_files
        self.show_captured_pieces = show_captured_pieces
        self.screen = screen
        self.screen_rect = screen.get_rect()

        self.current_player = players[True]

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.origin = origin if origin is not None else (0, 0)

        self.color_scheme = "default" # a key in the COLORS dictionary for the colors of the light and dark squares

        if board is None:
            board = chess.Board()

        self.board = self.create_gui_chess_board(board)

        self.source_position = None
        self.first_move_has_been_played = False

        self.game_over = False

        self.ai_playing = False

        print(f"Board rectangle is: {self.board.rect}")

    def create_gui_chess_board(self, board: chess.Board) -> ChessBoard:
        dimensions = self.get_board_dimensions()
        left = ((self.screen_width - dimensions[0]) / 2) + self.origin[0]
        top = ( (self.screen_height -dimensions[1]) / 2 ) + self.origin[1]

        chess_board = ChessBoard(
            left, top, dimensions[0], dimensions[1], 
            light_square_color=self.COLORS[self.color_scheme]["light"], dark_square_color=self.COLORS[self.color_scheme]["dark"], 
            board=board
        )
        return chess_board
    
    @property
    def light_square_color(self) -> tuple:
        return self.COLORS[self.color_scheme]['light']

    @property
    def dark_square_color(self) -> tuple:
        return self.COLORS[self.color_scheme]['dark']

    def __get_promotion_pieces_for_color(color):
        return [
            Piece("queen", "q", color), Piece("bishop", "b", color), Piece("knight", "n", color), 
            Piece("rook", "r", color)
        ]

    def draw_board(self):
        def draw_bordered_rectangle(rectangle: BorderedRectangle):
            pygame.draw.rect(self.screen, rectangle.border_color, rectangle.outer_rectangle, width=rectangle.outer_rectangle_border_width)
            pygame.draw.rect(self.screen, rectangle.border_color, rectangle.inner_rectangle, width=rectangle.inner_rectangle_border_width)
        
        def draw_captured_piece_images(rectangles: dict, margin_left: int=5):
            """
            rectangles is a dictionary with keys "b" and "w" and values of pygame.Rect objects
            in which to display the captured pieces of each side
            """
            difference = 0

            for color, captured_pieces in self.board.captured_pieces.items():
                for index, piece in enumerate(captured_pieces):
                    image = piece.get_image()
                    image_rect = image.get_rect()

                    difference += -(piece.value)

                    if color == "w":
                        # draw the pieces on black's side
                        rectangle = rectangles["b"]
                    else:
                        # draw the pieces on white's side
                        rectangle = rectangles["w"]

                    image = piece.get_image()
                    image_rect = image.get_rect()
                    image_rect.centery = rectangle.centery
                    image_rect.left = ( rectangle.left + margin_left ) + ( index * image_rect.width )

                    self.screen.blit(image, image_rect)

            if difference != 0:
                if difference > 0:
                    # black has captured more material than white, draw the absolute
                    # value of the difference next to the pieces captured
                    color = "w"
                    rectangle = rectangles[color]
                else:
                    # white has captured more material than black, draw the absolute value of 
                    # the difference next to the pieces captured
                    color = "b"
                    rectangle = rectangles[color]

                font = pygame.font.SysFont('helvetica', 15)
                text = font.render(f"+{abs(difference)}", True, self.dark_square_color )
                text_rect = text.get_rect()
                text_rect.centery = rectangle.centery
                text_rect.left = (rectangle.left + margin_left) + ( 15 * len(self.board.captured_pieces[color]) )
                
                self.screen.blit(text, text_rect)

        def draw_piece(piece: Piece, rect: pygame.Rect=None, center_coordinates: tuple=None):
            """
            draws a piece and sets its center either to that of the rect argument's center or the 
            center_coordinates argument passed
            """
            if center_coordinates is None and rect is None:
                raise ValueError("One of the following must not be None: (rect, center_coordinates)")
            elif not center_coordinates:
                center_coordinates = rect.center

            try:
                image = piece.get_image()
                image_rect = image.get_rect()
                image_rect.center = center_coordinates

                self.screen.blit(image, image_rect)
            except TypeError as e:
                raise e
            except FileNotFoundError as e:
                print(f"Image file for piece was not found")
                raise e

        def draw_text(text: str, text_color=None, font_size=15, font_family='helvetica', rect: pygame.Rect=None, center_coordinates: tuple=None):
            """
            Draws text <text> with center coordinates center_coordinates or the center of the rect object passed
            """
            if text_color is None:
                text_color = self.dark_square_color

            if rect is None and center_coordinates is None:
                raise ValueError("One of the following must not be None: (rect, center_coordinates)")
            
            if rect is not None and not isinstance(rect, pygame.Rect):
                raise ValueError("The rect argument must be a pygame.Rect object")

            if center_coordinates is not None and isinstance(center_coordinates,tuple):
                raise ValueError("The center_coordinates must be a tuple")

            if center_coordinates is None:
                center_coordinates = rect.center

            font = pygame.font.SysFont(font_family, font_size)

            text = font.render(text, True, text_color)
            text_rect = text.get_rect()
            text_rect.center = center_coordinates

            self.screen.blit(text, text_rect)

        def draw_rectangle(rectangle: pygame.Rect, background_color: tuple, border_width: int=0):
            pygame.draw.rect(self.screen, background_color, rectangle, width=border_width)
        
        ranks = self.board.squares

        # getting the coordinates of the left and top of the outermost border
        left = (self.screen_width - self.BOARD_OUTERMOST_BORDER_DIMENSIONS[0]) // 2 + self.origin[0]
        top = ( self.screen_width - self.BOARD_OUTERMOST_BORDER_DIMENSIONS[1] ) // 2 + self.origin[1]

        outermost_border_width = self.BOARD_OUTERMOST_BORDER_DIMENSIONS[0]
        outermost_border_height = self.BOARD_OUTERMOST_BORDER_DIMENSIONS[1]

        # the difference in sizes between the inner and outer rectangles
        size = outermost_border_width - self.BOARD_DIMENSIONS[0] - 2
        
        board_bordered_rectangle = BorderedRectangle(
            left, top, outermost_border_width, outermost_border_height, 
            self.COLORS["white"], self.dark_square_color, size
        )
        draw_bordered_rectangle(board_bordered_rectangle)

        # draw the inner rectangle with a different color
        pygame.draw.rect(
            self.screen, board_bordered_rectangle.border_color, board_bordered_rectangle.inner_rectangle
        )

        board_top_left = self.board.rect.topleft
        board_bottom_left = self.board.rect.bottomleft
        board_square_size = self.board.square_size

        for i, rank in enumerate(ranks):
            for j, square in enumerate(rank):
                if square is self.board.previous_move_square:
                    pygame.draw.rect( self.screen, self.board.previous_square_highlight_color, square )
                elif square is self.board.current_move_square:
                    pygame.draw.rect( self.screen, self.board.current_square_highlight_color, square )
                else:
                    pygame.draw.rect( self.screen, square.background_color, square )

                if square.is_possible_move and self.board.move_hints:
                    if not square.piece: # draw a simple circle if the square doesn't have a piece on it
                        pygame.draw.circle(
                            self.screen, self.possible_move_highlight_color, 
                            square.center, board_square_size * 0.25
                        )
                    else: # draw two circles around the piece
                        pygame.draw.circle(
                            self.screen, self.possible_move_highlight_color, 
                            square.center, board_square_size * 0.5
                        )
                        pygame.draw.circle(
                            self.screen, square.background_color, 
                            square.center, board_square_size * 0.45
                        )

                if square.piece:
                    try:
                        draw_piece(square.piece, square)
                    except TypeError as e:
                        print(f"The square's piece is: ")
                        print(square.piece)
                        raise e
                    except FileNotFoundError as e:
                        print(f"Error on the square on the {i}th rank and the {j}th rank")
                        raise e

                if self.show_ranks_and_files and (square.rank_number == 0 or square.file_number == 0):
                    font_size = 10

                    square_rank_number = square.rank_number
                    square_file_number = square.file_number

                    color = (
                        self.dark_square_color 
                        if square.background_color == self.light_square_color else 
                        self.light_square_color
                    )

                    if square_rank_number == 0:
                        # write the file numbers in the squares on the first rank
                        character = str(square.get_file()).upper()
                        _rect = pygame.Rect(
                            square.right - font_size, square.bottom - font_size, 
                            font_size, font_size
                        )
                        draw_text(character, color, rect=_rect, font_size=10)
                        
                    if square_file_number == 0:
                        # write the rank numbers in the squares on the first file
                        character = str(square.get_rank())
                        _rect = pygame.Rect(
                            square.left, square.top, font_size, font_size
                        )
                        draw_text(character, color, rect=_rect, font_size=10)
                        

            captured_pieces_rectangle_height = 20

            captured_pieces_rectangles = {
                "b": pygame.Rect( 
                    board_top_left[0], board_top_left[1] - captured_pieces_rectangle_height, self.board.rect.width
                    , captured_pieces_rectangle_height
                ),
                "w": pygame.Rect( 
                    board_bottom_left[0], board_bottom_left[1] + 20, self.board.rect.width
                    , captured_pieces_rectangle_height
                )
            }

            draw_captured_piece_images(captured_pieces_rectangles)

        transparent_backdrop = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA
        )

        # print("Created transparent backdrop")

        # if self.game_over:
        #     transparent_backdrop.fill((0, 0, 0, 140))
        #     self.screen.blit(transparent_backdrop, (0, 0))

        #     text_color = (255, 255, 255)
        #     font_size = 40
        #     font = pygame.font.SysFont('helvetica', font_size)

        #     for i in range(2):
        #         # display texts (Game over and the result i.e. stalemate, draw, checkmate etc.)
        #         if i == 0:
        #             text_content = "Game over"
        #         else:
        #             if self.board.board.is_checkmate():
        #                 winner = not self.board.board.turn
        #                 text_content = f"{'White' if winner else 'Black'} won by checkmate"

        #             if self.board.board.is_stalemate():
        #                 text_content = "Draw by stalemate"


        #         text = font.render(text_content, True, text_color )
        #         text_rect = text.get_rect()
        #         # display in the middle of the screen
        #         text_rect.center = ( self.screen_width // 2, self.screen_height // 2 + ( font_size * i ) )

        #     self.screen.blit(text, text_rect)

        # if 1:
        #     print("Drawing promotion pieces")
        #     # promotion
        #     transparent_backdrop.fill((0, 0, 0, 140))
        #     self.screen.blit(transparent_backdrop, (0, 0))
            
        #     pawn_promotion_rectangle = pygame.Rect(
        #         0, 0, board_square_size * 4, board_square_size
        #     )
        #     board_rectangle = self.board.rect

        #     for i in range(2):
        #         pawn_promotion_rectangle.centerx = board_rectangle.centerx
        #         pawn_promotion_rectangle.centery = (
        #             self.board.squares[0][0].centery 
        #             if i == 0 else 
        #             self.board.squares[7][0].centery
        #         )

        #         promotion_pieces = ChessGame.__get_promotion_pieces_for_color("w" if i == 0 else "b")

        #         for index, piece in enumerate(promotion_pieces):
        #             square = pygame.Rect(
        #                 pawn_promotion_rectangle.left + (index * board_square_size), 
        #                 pawn_promotion_rectangle.centery, board_square_size, board_square_size
        #             )
        #             draw_rectangle(square, BLACK_COLOR if i==0 else WHITE_COLOR, 1 )
        #             draw_piece(piece, rect=square)

    def play_sound(self):
        if self.board.board.is_checkmate():
            if not self.game_over:
                pygame.mixer.Sound.play(self.SOUNDS["checkmate"])
                self.game_over = True

        elif self.board.board.is_check():
            pygame.mixer.Sound.play(self.SOUNDS["check"])

        elif self.board.board.is_stalemate():
            self.game_over = True
        else:
            pygame.mixer.Sound.play(self.SOUNDS["move"])
        
    def get_board_dimensions(self) -> tuple:
        return self.BOARD_DIMENSIONS

    @property
    def possible_move_highlight_color(self):
        return self.COLORS["move_highlight"]

    def play(self, source_coordinates: tuple=None, destination_coordinates: tuple=None):
        current_player = self.current_player

        if isinstance(current_player, ai_players.Player):
            # it's the user's turn to play
            if self.board.rect.collidepoint(*source_coordinates) and self.board.rect.collidepoint(*destination_coordinates):
                self.board.play(source_coordinates, destination_coordinates)

                if not self.first_move_has_been_played:
                    self.first_move_has_been_played = True

                self.play_sound()
        else:
            current_player.make_move(self.board)
            
            if not self.first_move_has_been_played:
                    self.first_move_has_been_played = True
                    
            self.play_sound()

            self.ai_playing = False

        self.set_current_player()

    def set_current_player(self):
        self.current_player = self.players[ self.board.board.turn ]

    def start(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.click_handler(pygame.mouse.get_pos())

            self.screen.fill( self.COLORS["white"] )

            self.draw_board()

            if isinstance(self.current_player, ai_players.AIPlayer):
                if not self.ai_playing:
                    # to prevent the thread from being created multiple times
                    self.ai_playing = True
                    self.play_in_thread()

            pygame.display.flip()

        pygame.quit()
        print("Window closed")
    
    def play_in_thread(self):
        thread = threading.Thread(target=lambda: self.play())
        thread.start()
        return thread

    def click_handler(self, position):
        current_player = self.current_player

        if isinstance(current_player, ai_players.Player):
            # user
            if self.source_position is None:
                # user is initiating a move
                self.possible_moves = self.board.get_possible_moves(position)
                self.source_position = position if self.possible_moves else None
            else:
                # user has already clicked on a piece they want to move
                destination_square = [ square for square in self.possible_moves if square.collidepoint(position) ]

                if not destination_square:
                    # removing the move hints
                    self.board.get_possible_moves(self.source_position, remove_hints=True)
                    self.source_position = None
                else:
                    destination_square = destination_square[0]
                    # removing the move hints
                    self.board.get_possible_moves(self.source_position, remove_hints=True)

                    self.play(self.source_position, position)
                    
                    self.source_position = None
