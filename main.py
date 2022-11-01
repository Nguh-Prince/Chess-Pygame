from curses.ascii import islower
import pygame
import chess
from gui_components.board import ChessBoard

from gui_components.pieces import Piece

pygame.init()

screen = pygame.display.set_mode([500, 500])

SOURCE_POSITION = None
DESTINATION_POSITION = None
PREVIOUSLY_CLICKED_POSITION = None
POSSIBLE_MOVES = []

running = True

board = chess.Board()

CELL_HEIGHT = 500 / 8
CELL_WIDTH = 500 / 8
LIGHT_COLOR = (245, 245, 245)
DARK_COLOR = ( 100, 100, 100 )

chess_board = ChessBoard(
    0, 0, 500, 500, 0, 0, board=board, square_size=CELL_HEIGHT
)

def click_handler(position):
    global SOURCE_POSITION, POSSIBLE_MOVES  

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
            chess_board.play( SOURCE_POSITION, position )
            SOURCE_POSITION = None

def draw_board(board: chess.Board, possible_moves=None):
    string = board.__str__()
    ranks_inverted = string.split('\n')[::-1]

    for i, rank in enumerate(ranks_inverted):
        squares = rank.split(' ')

        for j, square in enumerate(squares):
            
            color = LIGHT_COLOR if (i+j) % 2 == 0 else DARK_COLOR
            rect = pygame.Rect( j*CELL_HEIGHT, i*CELL_WIDTH, CELL_HEIGHT, CELL_WIDTH )
            pygame.draw.rect(screen, color, rect)

            if square != '.':
                notation = square.lower()
                color = "b" if square.isupper() else "w"
                
                piece = Piece(notation, notation, color)
                piece_image = piece.get_image()
                screen.blit(piece_image, rect.topleft)

                # if rect.collidepoint(MOUSE_CLICKED_POSITION) and not possible_moves:
                if 1:
                    chess_square = chess.square(j, 8-i)

                    # getting the possible moves from the selected square
                    possible_piece_moves = [ move.to_square for move in board.legal_moves if move.from_square == chess_square ]
                    # draw_board(board, possible_piece_moves)

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

        if event.type == pygame.MOUSEBUTTONUP:
            MOUSE_CLICKED_POSITION = pygame.mouse.get_pos()
            click_handler(MOUSE_CLICKED_POSITION)

    screen.fill( (255, 255, 255) )
    
    # draw_board(board)
    draw_chessboard(chess_board)

    pygame.display.flip()

pygame.quit()