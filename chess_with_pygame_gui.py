import chess
import chess.pgn

import pygame
from pygame import mixer
import pygame_gui

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_panel import UIPanel
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.elements.ui_image import UIImage

from gui_components.board import ChessBoard
from gui_components.components import BorderedRectangle

mixer.init()

LIGHT_COLOR = (245, 245, 245)
DARK_COLOR = (10, 100, 20)
WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)

players = {
    True: "user",
    False: "user"
}

turns_taken = {
    True: False, # set 
    False: False
}

move_sound = mixer.Sound("sound_effects/piece_move.mp3")
check_sound = mixer.Sound("sound_effects/check.mp3")
checkmate_sound = mixer.Sound("sound_effects/checkmate.mp3")

SOURCE_POSITION = None
DESTINATION_POSITION = None
PREVIOUSLY_CLICKED_POSITION = None
POSSIBLE_MOVES = []
TURN = True
IS_FIRST_MOVE = True


class ChessApp:
    def __init__(self, color="white"):
        pygame.init()

        self.root_window_surface = pygame.display.set_mode((912, 600))

        self.screen = pygame.Surface((912, 600)).convert()
        self.screen.fill(pygame.Color('#505050'))
        self.ui_manager = UIManager((912, 600))
        self.clock = pygame.time.Clock()
        self.is_running = True

        self.pgn_panel = UIPanel(
            pygame.Rect(576+24, 12, 300, 576),
            starting_layer_height=4,
            manager=self.ui_manager
        )
        self.pgn_text = UITextBox(
            relative_rect=pygame.Rect((0, 0), self.pgn_panel.get_container().get_size()),
            html_text="",
            container=self.pgn_panel
        )

        self.board = chess.Board()
        self.chess_board = ChessBoard(
            12, 12, 576, 576, 0, 0, 
            board=self.board, flipped=color != "white"
        )

        self.draw_chessboard()

    def draw_bordered_rectangle(self, rectangle: BorderedRectangle, screen):
        pygame.draw.rect( screen, rectangle.border_color, rectangle.outer_rectangle, width=rectangle.outer_rectangle_border_width )
        pygame.draw.rect( screen, rectangle.background_color, rectangle.inner_rectangle, width=rectangle.inner_rectangle_border_width )

    def draw_chessboard(self, board: ChessBoard=None, flip=False):
        if board is None:
            board = self.chess_board

        ranks = board.squares

        board_bordered_rectangle = BorderedRectangle(12, 12, 576, 576, WHITE_COLOR, DARK_COLOR, 48)
        self.draw_bordered_rectangle(board_bordered_rectangle, self.screen)

        pygame.draw.rect( 
            self.screen, board_bordered_rectangle.border_color, board_bordered_rectangle.inner_rectangle, 
            width=1
        )

        board_top_left = board.rect.topleft
        board_top_right = board.rect.topright
        board_bottom_left = board.rect.bottomleft

        for i, rank in enumerate(ranks):
            rank_number = ChessBoard.RANKS[ 7 - i ]
            file_letter = ChessBoard.RANKS[i]
            
            font_size = 15 # font size for the ranks and files
            
            # add the text rectangle on the left and right of the board
            font = pygame.font.SysFont('helvetica', font_size)

            # render the ranks (1-8)
            for _i in range(1):
                if _i == 0:
                    _rect = pygame.Rect(
                        board_top_left[0] - font_size, board_top_left[1] + (i*board.square_size), 
                        font_size, board.square_size
                    )
                else:
                    _rect = pygame.Rect(
                        board_top_right[0], board_top_right[1] + (i*board.square_size),
                        font_size, board.square_size
                    )

                text = font.render(f"{rank_number}", True, DARK_COLOR)
                text_rect = text.get_rect()
                text_rect.center = _rect.center

                self.screen.blit(text, text_rect)

            # render the files A-H
            for _i in range(1):
                if _i == 0:
                    _rect = pygame.Rect(
                        board_top_left[0] + (i*board.square_size), board_top_left[1] - font_size, 
                        board.square_size, font_size
                    )
                else:
                    _rect = pygame.Rect(
                        board_top_left[0] + (i*board.square_size), board_bottom_left[1], 
                        board.square_size, font_size
                    )
                
                text = font.render(f"{file_letter}", True, DARK_COLOR)
                text_rect = text.get_rect()
                text_rect.center = _rect.center

                self.screen.blit(text, text_rect)
                
            for j, square in enumerate(rank):
                if square is board.previous_move_square:
                    pygame.draw.rect( self.screen, board.previous_square_highlight_color, square )
                elif square is board.current_move_square:
                    pygame.draw.rect( self.screen, board.current_square_highlight_color, square )
                else:
                    pygame.draw.rect( self.screen, square.background_color, square )
                
                if square.piece:
                    try:
                        image = square.piece.get_image()
                        image_rect = image.get_rect()
                        image_rect.center = square.center

                        self.screen.blit( image, image_rect )
                    except TypeError as e:
                        raise e
                    except FileNotFoundError as e:
                        print(f"Error on the square on the {i}th rank and the {j}th rank")
                        raise e
                
                if square.is_possible_move and board.move_hints:
                    # draw a circle in the center of the square
                    pygame.draw.circle( 
                        self.screen, (50, 50, 50), 
                        square.center,
                        board.square_size*0.25
                    )

    def play_sound(self, board=None):
        if not board:
            board = self.board

        if board.is_checkmate():
            mixer.Sound.play(checkmate_sound)
        
        elif board.is_check():
            mixer.Sound.play(check_sound)
        
        elif board.is_stalemate():
            pass
        
        else:
            mixer.Sound.play(move_sound)

    def play(self, source_coordinates: tuple=None, destination_coordinates: tuple=None):
        global TURN, IS_FIRST_MOVE
        board = self.board

        turn = board.turn

        turns_taken[turn] = not turns_taken[turn]
        print(f"Setting {turns_taken[turn]} to {not turns_taken[turn]}")

        if source_coordinates and destination_coordinates:
            # user to play
            print("User is making move")
            self.chess_board.play(source_coordinates, destination_coordinates)
            self.play_sound(board)
            TURN = not TURN

        if IS_FIRST_MOVE:
            IS_FIRST_MOVE = False
        
        turns_taken[turn] = not turns_taken[turn]
        print(f"Setting {turns_taken[turn]} to {not turns_taken[turn]}")

        self.pgn_text.set_text(
            str(chess.pgn.Game().from_board(self.board))
        )

    def click_handler(self, position):
        global SOURCE_POSITION, POSSIBLE_MOVES, TURN

        current_player = players[TURN]

        if isinstance(current_player, str):
            if SOURCE_POSITION is None:
                POSSIBLE_MOVES = self.chess_board.get_possible_moves(position)
                SOURCE_POSITION = position if POSSIBLE_MOVES else None

                print("Getting the source square. The square is: ")
                print(SOURCE_POSITION)
            else:
                # getting the squares in the possible destinations that correspond to the clicked point
                destination_square = [ square for square in POSSIBLE_MOVES if square.collidepoint(position) ]

                if not destination_square:
                    self.chess_board.get_possible_moves(SOURCE_POSITION, remove_hints=True)
                    SOURCE_POSITION = None
                else:
                    destination_square = destination_square[0]
                    print(f"In main.py, about to play, the source and destination are {SOURCE_POSITION} and {position} respectively")
                    self.chess_board.get_possible_moves(SOURCE_POSITION, remove_hints=True)
                    
                    # self.chess_board.play( SOURCE_POSITION, position )
                    self.play(SOURCE_POSITION, position)

                    SOURCE_POSITION = None


    def run(self):
        while self.is_running:
            time_delta = self.clock.tick(60)/1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    MOUSE_CLICKED_POSITION = pygame.mouse.get_pos()
                    self.click_handler(MOUSE_CLICKED_POSITION)

                self.ui_manager.process_events(event)

            self.draw_chessboard()

            self.ui_manager.update(time_delta)

            self.root_window_surface.blit(self.screen, (0, 0))
            self.ui_manager.draw_ui(self.root_window_surface)

            pygame.display.update()

if __name__ == '__main__':
    app = ChessApp()
    app.run()