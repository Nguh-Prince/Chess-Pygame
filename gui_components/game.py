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
    BOARD_OUTERMOST_BORDER_DIMENSIONS = (480, 480)

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
        
        def draw_captured_images(rectangle: pygame.Rect, captured_pieces_list, margin_left: int=5, difference: int=None):
            for index, piece in enumerate(captured_pieces_list):
                image = piece.get_image()
                image_rect = image.get_rect()
                image_rect.centery = rectangle.centery
                image_rect.left = ( rectangle.left + margin_left ) + ( index * image_rect.width )

                self.screen.blit(image, image_rect)

            if difference is not None:
                print("In draw_captured_images() the difference is not None")
                font = pygame.font.SysFont('helvetica', 15)
                text = font.render(f"+{difference}", True, self.dark_square_color )
                text_rect = text.get_rect()
                text_rect.centery = rectangle.centery
                text_rect.left = (rectangle.left + margin_left) + ( 15 * len(captured_pieces_list) )
                
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
        board_top_right = self.board.rect.topright
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
    
    def play_sound(self):
        if self.board.board.is_checkmate():
            pygame.mixer.Sound.play(self.SOUNDS["checkmate"])

        elif self.board.board.is_check():
            pygame.mixer.Sound.play(self.SOUNDS["check"])

        else:
            pygame.mixer.Sound.play(self.SOUNDS["move"])
        
    def get_board_dimensions(self) -> tuple:
        return self.BOARD_DIMENSIONS

    @property
    def possible_move_highlight_color(self):
        return self.COLORS["move_highlight"]

    def start(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.screen.fill( self.COLORS["white"] )

            self.draw_board()

            pygame.display.flip()

        pygame.quit()
        print("Window closed")

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode( [500, 500] )

board = chess.Board()

players = {
    True: "user",
    False: ai_players.PlayerWithEvaluation(board, "b")
}

game = ChessGame(screen, players, board=board)
game.start()
