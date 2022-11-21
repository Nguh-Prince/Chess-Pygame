import chess

import pygame

from pygame import mixer

mixer.init()

from gui_components.board import ChessBoard
from gui_components.components import BorderedRectangle

from ai import players as ai_players

pygame.init()

screen = pygame.display.set_mode([500, 500])

board = chess.Board()

# A dictionary of the different players in the game. True corresponds to white and 
# False to black
players = { 
    True: "user",
    False: "user"
}

turns_taken = {
    True: False, # set to True if white has already started playing 
    False: False # set to True if black has already started playing
}

# the different sounds for the moves
move_sound = mixer.Sound("sound_effects/piece_move.mp3")
check_sound = mixer.Sound("sound_effects/check.mp3")
checkmate_sound = mixer.Sound("sound_effects/checkmate.mp3")

SOURCE_POSITION = None
DESTINATION_POSITION = None
PREVIOUSLY_CLICKED_POSITION = None
POSSIBLE_MOVES = []
TURN = True
IS_FIRST_MOVE = True

running = True

LIGHT_COLOR = (245, 245, 245) # color of the light squares
DARK_COLOR = ( 100, 100, 100 ) # color of the dark squares
WHITE_COLOR = (255, 255, 255) # white
BLACK_COLOR = (0, 0, 0) # black

chess_board = ChessBoard(  # creating a new ChessBoard object
    50, 50, 400, 400, 0, 0, board=board
)

def draw_bordered_rectangle(rectangle: BorderedRectangle, screen):
    pygame.draw.rect( screen, rectangle.border_color, rectangle.outer_rectangle, width=rectangle.outer_rectangle_border_width )
    pygame.draw.rect( screen, rectangle.background_color, rectangle.inner_rectangle, width=rectangle.inner_rectangle_border_width )

def draw_chessboard(board: ChessBoard):
    """
    Draw the chess board on the pygame window
    """
    ranks = board.squares # get the rows of the board

    # a rectangle enclosing the board and the files and ranks labels
    board_bordered_rectangle = BorderedRectangle(25, 25, 450, 450, WHITE_COLOR, DARK_COLOR, 48)
    draw_bordered_rectangle(board_bordered_rectangle, screen)

    # draw the inner rectangle of the bordered rectangle with the same color 
    # as that of the dark squares
    pygame.draw.rect( 
        screen, board_bordered_rectangle.border_color, board_bordered_rectangle.inner_rectangle, 
        width=1
    )

    board_top_left = board.rect.topleft
    board_top_right = board.rect.topright
    board_bottom_left = board.rect.bottomleft

    for i, rank in enumerate(ranks):
        rank_number = ChessBoard.RANKS[ 7 - i ]
        file_letter = ChessBoard.FILES[i]
        
        font_size = 15 # font size for the ranks and files
        
        # add the text rectangle on the left and right of the board
        font = pygame.font.SysFont('helvetica', font_size)

        # render the ranks (1-8)
        for _i in range(2):
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

            screen.blit(text, text_rect)

        # render the files A-H
        for _i in range(2):
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

            screen.blit(text, text_rect)
            
        for j, square in enumerate(rank):
            if square is board.previous_move_square:
                # highlight source square of the latest move
                pygame.draw.rect( screen, board.previous_square_highlight_color, square )
            elif square is board.current_move_square:
                # highlight the destination square of the latest move
                pygame.draw.rect( screen, board.current_square_highlight_color, square )
            else:
                pygame.draw.rect( screen, square.background_color, square )
            
            if square.piece:
                # draw the piece on the square
                try:
                    image = square.piece.get_image()
                    image_rect = image.get_rect()
                    image_rect.center = square.center

                    screen.blit( image, image_rect )
                except TypeError as e:
                    raise e
                except FileNotFoundError as e:
                    print(f"Error on the square on the {i}th rank and the {j}th rank")
                    raise e
            
            if square.is_possible_move and board.move_hints:
                # draw a circle in the center of the square to highlight is as a possible move
                pygame.draw.circle( 
                    screen, (50, 50, 50), 
                    square.center,
                    board.square_size*0.25
                )

def play_sound(board):
    """
    Play sound after move based on move type
    """
    if board.is_checkmate():
        mixer.Sound.play(checkmate_sound)
    
    elif board.is_check():
        mixer.Sound.play(check_sound)
    
    elif board.is_stalemate():
        pass
    
    else:
        mixer.Sound.play(move_sound)

def play(source_coordinates: tuple=None, destination_coordinates: tuple=None):
    """
    Make a move on the board based on the source and destination coordinates if a user is playing
    """
    global board, TURN, IS_FIRST_MOVE, chess_board

    turn = board.turn

    player = players[turn]
    turns_taken[turn] = not turns_taken[turn]
    print(f"Setting {turns_taken[turn]} to {not turns_taken[turn]}")

    if not isinstance(player, str):
        # AI model to play
        player.make_move(chess_board)
        play_sound(board)
        
        TURN = not TURN
        
        if isinstance(players[TURN], ai_players.AIPlayer):
            # if the next player is an AI, automatically play
            print("Next player is AI, making a move for them automaically")
            # sleep(5)
    else:
        if source_coordinates and destination_coordinates:
            # user to play
            print("User is making move")
            chess_board.play(source_coordinates, destination_coordinates)
            play_sound(board)
            TURN = not TURN

    if IS_FIRST_MOVE:
        IS_FIRST_MOVE = False
    
    turns_taken[turn] = not turns_taken[turn]
    print(f"Setting {turns_taken[turn]} to {not turns_taken[turn]}")


def click_handler(position):
    """
    Handle the click events of the game
    """
    global SOURCE_POSITION, POSSIBLE_MOVES, TURN

    if chess_board.rect.collidepoint(position): # if position is in the board
        current_player = players[TURN]

        if isinstance(current_player, str):
            if SOURCE_POSITION is None:
                POSSIBLE_MOVES = chess_board.get_possible_moves(position)
                SOURCE_POSITION = position if POSSIBLE_MOVES else None
            else:
                # getting the squares in the possible destinations that correspond to the clicked point
                destination_square = [ square for square in POSSIBLE_MOVES if square.collidepoint(position) ]

                if not destination_square:
                    chess_board.get_possible_moves(SOURCE_POSITION, remove_hints=True)
                    SOURCE_POSITION = None
                else:
                    destination_square = destination_square[0]
                    print(f"In main.py, about to play, the source and destination are {SOURCE_POSITION} and {position} respectively")
                    chess_board.get_possible_moves(SOURCE_POSITION, remove_hints=True)
                    
                    # chess_board.play( SOURCE_POSITION, position )
                    play(SOURCE_POSITION, position)
                    SOURCE_POSITION = None
                    
                    current_player = players[TURN]

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            MOUSE_CLICKED_POSITION = pygame.mouse.get_pos()
            click_handler(MOUSE_CLICKED_POSITION)

    screen.fill( (255, 255, 255) )
    
    draw_chessboard(chess_board)

    pygame.display.flip()

pygame.quit()