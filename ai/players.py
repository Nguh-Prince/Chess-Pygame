"""
The ai algorithms that can be chosen to play a game against
"""
import copy

import chess
import random
from gui_components.board import ChessBoard

# class UserPlayer:
#     def __init__(self, board) -> None:
#         self.board = board
#         pass

class AIPlayer:
    def __init__(self, board: chess.Board, color: str) -> None:
        self.board = board
        self.color = color

    def get_legal_moves(self, board: chess.Board=None):
        if not board:
            board = self.board

        return list(board.legal_moves)

    def play(self) -> chess.Move:
        """
        Selects a move using some technique from the list of legal moves
        """
        legal_moves = self.get_legal_moves()
        
        return legal_moves[0]

    def false_move(self):
        # make a copy of the board for move testing
        board_copy = copy.deepcopy(self.board)

        move = self.play()
        
        board_copy.push(move)

    def evaluate_board(self, board: chess.Board=None):
        pass

    def make_move(self, chess_board: ChessBoard):
        move = self.play()

        chess_board._play(move=move)

class RandomPlayer(AIPlayer):
    def play(self) -> chess.Move:
        legal_moves = list(self.board.legal_moves)

        move = random.choice(legal_moves)

        return move

class PlayerWithEvaluation(AIPlayer):
    def play(self) -> chess.Move:
        return super().play()