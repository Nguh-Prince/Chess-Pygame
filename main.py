from time import sleep

import pygame
import chess
from gui_components.board import ChessBoard

from ai.players import AIPlayer, RandomPlayer

pygame.init()

screen = pygame.display.set_mode([500, 500])

board = chess.Board()

players = {
    True: "user",
    False: RandomPlayer(board)
}

SOURCE_POSITION = None
DESTINATION_POSITION = None
PREVIOUSLY_CLICKED_POSITION = None
POSSIBLE_MOVES = []
TURN = True
IS_FIRST_MOVE = True

running = True

CELL_HEIGHT = 500 / 8
CELL_WIDTH = 500 / 8
LIGHT_COLOR = (245, 245, 245)
DARK_COLOR = ( 100, 100, 100 )

chess_board = ChessBoard(
    0, 0, 500, 500, 0, 0, board=board, square_size=CELL_HEIGHT
)

def play(source_coordinates: tuple=None, destination_coordinates: tuple=None):
    global board, TURN

    if board.is_checkmate():
        print("The game is over, checkmate")
        return

    if board.is_stalemate():
        print("The game is over, stalemate")
        return

    turn = board.turn

    player = players[turn]

    if not isinstance(player, str):
        # AI model to play
        print("AI is making move")
        player.make_move(chess_board)
        TURN = not TURN
        
        if isinstance(players[TURN], AIPlayer):
            # if the next player is an AI, automatically play
            sleep(5)
            play()
    else:
        if source_coordinates and destination_coordinates:
            # user to play
            print("User is making move")
            chess_board.play(source_coordinates, destination_coordinates)
            TURN = not TURN
        else: 
            pass


def click_handler(position):
    global SOURCE_POSITION, POSSIBLE_MOVES, TURN

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

                if not isinstance(current_player, str):
                    # automatically play with the AI if it is their turn
                    play()
    else:
        play()

def draw_chessboard(board: ChessBoard):
    cell_height = board.square_size
    cell_width = board.square_size

    for i, rank in enumerate(board.squares):
        for j, square in enumerate(rank):
            pygame.draw.rect( screen, square.background_color, square )

            if square.piece:
                try:
                    screen.blit( square.piece.get_image(), square.topleft )
                except TypeError as e:
                    print(f"The square's piece is: ")
                    print(square.piece)
                    raise e
                except FileNotFoundError as e:
                    print(f"Error on the square on the {i}th rank and the {j}th rank")
                    raise e
            
            if square.is_possible_move and board.move_hints:
                # draw a circle in the center of the square
                pygame.draw.circle( 
                    screen, (50, 50, 50), 
                    square.center,
                    board.square_size*0.25
                )

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            MOUSE_CLICKED_POSITION = pygame.mouse.get_pos()
            click_handler(MOUSE_CLICKED_POSITION)

    screen.fill( (255, 255, 255) )
    
    # draw_board(board)
    draw_chessboard(chess_board)

    if not isinstance(players[TURN], str) and IS_FIRST_MOVE:
        play()

    pygame.display.flip()

pygame.quit()