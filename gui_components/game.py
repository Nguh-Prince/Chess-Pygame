import threading
import chess

# from ..data_structures import trees
from ai import players as ai_players
from gui_components.board import ChessBoard
import pygame

# pygame.init()
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

        # for key, player in players.items():
        #     if player.color == "w":
        #         self.current_player = None
        self.current_player = players[True]

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.origin = origin if origin is not None else (0, 0)

        self.color_scheme = "default" # a key in the COLORS dictionary for the colors of the light and dark squares

        if board is None:
            board = chess.Board()

        self.create_chess_board(board)

        self.source_position = None
        self.first_move_has_been_played = False

        self.game_over = False

    def create_chess_board(self, board: chess.Board) -> ChessBoard:
        dimensions = self.get_board_dimensions()
        left = ((self.screen_width - dimensions[0]) / 2) + self.origin[0]
        top = ( (self.screen_height -dimensions[1]) / 2 ) + self.origin[1]

        chess_board = ChessBoard(
            left, top, dimensions[0], dimensions[1], 
            light_square_color=self.COLORS[self.color_scheme]["light"], dark_square_color=self.COLORS[self.color_scheme]["dark"], 
            board=board
        )

        self.board = chess_board

        return chess_board
    
    @property
    def light_square_color(self) -> tuple:
        return self.COLORS[self.color_scheme]['light']

    @property
    def dark_square_color(self) -> tuple:
        return self.COLORS[self.color_scheme]['dark']

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
            rank_number = ChessBoard.RANKS[7-i] if not self.board.is_flipped else ChessBoard.RANKS[i]
            file_letter = ChessBoard.FILES[i] if not self.board.is_flipped else ChessBoard.FILES[7-i]

            if self.show_ranks_and_files:
                font_size = 20

                font = pygame.font.SysFont('helvetica', font_size - 5)

                for _i in range(2):
                    if _i == 0:
                        # drawing rank number (1-8)
                        _rect = pygame.Rect(
                            board_top_left[0] - font_size, board_top_left[1] + ( i * board_square_size ), 
                            font_size, board_square_size
                        )
                        character = str(rank_number)
                    else:
                        # drawing file letter (A-H)
                        _rect = pygame.Rect(
                            board_bottom_left[0] + (i*board_square_size), board_bottom_left[1], 
                            board_square_size, font_size
                        )
                        character = file_letter
                    
                    text = font.render(character, True, self.dark_square_color)
                    text_rect = text.get_rect()
                    text_rect.center = _rect.center

                    self.screen.blit(text, text_rect)

            for j, square in enumerate(rank):
                if square is self.board.previous_move_square:
                    pygame.draw.rect( self.screen, self.board.previous_square_highlight_color, square )
                elif square is self.board.current_move_square:
                    pygame.draw.rect( self.screen, self.board.current_square_highlight_color, square )
                else:
                    pygame.draw.rect( self.screen, square.background_color, square )

                if square.piece:
                    try:
                        image = square.piece.get_image()
                        image_rect = image.get_rect()
                        image_rect.center = square.center

                        self.screen.blit( image, image_rect )
                    except TypeError as e:
                        print(f"The square's piece is: ")
                        print(square.piece)
                        raise e
                    except FileNotFoundError as e:
                        print(f"Error on the square on the {i}th rank and the {j}th rank")
                        raise e

                if square.is_possible_move and self.board.move_hints:
                    pygame.draw.circle(
                        self.screen, self.possible_move_highlight_color, 
                        square.center, board_square_size * 0.25
                    )

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

    def play_sound(self):
        if self.board.board.is_checkmate():
            if not self.game_over:
                pygame.mixer.Sound.play(self.SOUNDS["checkmate"])
                self.game_over = True

        elif self.board.board.is_check():
            pygame.mixer.Sound.play(self.SOUNDS["check"])

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
