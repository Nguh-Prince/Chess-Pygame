import threading

import chess

import pygame

from pygame import mixer

mixer.init()

from gui_components.board import ChessBoard

from ai import players as ai_players

pygame.init()

screen = pygame.display.set_mode([500, 500])

board = chess.Board()

players = {
    True: "user",
    False: ai_players.MiniMaxPlayer(board, "b")
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

running = True

CELL_HEIGHT = 500 / 8
CELL_WIDTH = 500 / 8
LIGHT_COLOR = (245, 245, 245)
DARK_COLOR = ( 100, 100, 100 )

chess_board = ChessBoard(
    0, 0, 500, 500, 0, 0, board=board, square_size=CELL_HEIGHT
)

def draw_chessboard(board: ChessBoard):
    cell_height = board.square_size
    cell_width = board.square_size

    for i, rank in enumerate(board.squares):
        for j, square in enumerate(rank):
            if not square is board.previous_move_square:
                pygame.draw.rect( screen, square.background_color, square )
            else:
                pygame.draw.rect( screen, board.previous_square_highlight_color, square )

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


def play(source_coordinates: tuple=None, destination_coordinates: tuple=None):
    global board, TURN, IS_FIRST_MOVE, chess_board

    if board.is_checkmate():
        print("The game is over, checkmate")
        mixer.Sound.play(checkmate_sound)
        return

    if board.is_check():
        print("Check")
        mixer.Sound.play(check_sound)

    if board.is_stalemate():
        print("The game is over, stalemate")
        return

    turn = board.turn

    player = players[turn]
    turns_taken[turn] = not turns_taken[turn]
    print(f"Setting {turns_taken[turn]} to {not turns_taken[turn]}")

    if not isinstance(player, str):
        # AI model to play
        player.make_move(chess_board)
        mixer.Sound.play(move_sound)
        
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
            mixer.Sound.play(move_sound)
            TURN = not TURN

    if IS_FIRST_MOVE:
        IS_FIRST_MOVE = False
    
    turns_taken[turn] = not turns_taken[turn]
    print(f"Setting {turns_taken[turn]} to {not turns_taken[turn]}")


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
    # else:
    #     play()
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
        print("It is the first move and there is no human player")
        play()
    elif not isinstance(players[TURN], str) and not turns_taken[TURN]:
        print("AI's turn to play")
        thread = threading.Thread(target=lambda: play())
        thread.start()
        # play()

    pygame.display.flip()

pygame.quit()