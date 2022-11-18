"""
The ai algorithms that can be chosen to play a game against
"""
import copy
import random
import re
from pprint import pprint

import chess
from gui_components.board import ChessBoard
from gui_components.pieces import Piece

from data_structures.trees import Node, Tree

class Player:
    def __init__(self, name: str, color: str, board: chess.Board) -> None:
        self.name = name
        self.color = color
        self.board = board

    def __str__(self) -> str:
        return self.name

# class UserPlayer:
#     def __init__(self, board) -> None:
#         self.board = board
#         pass

class MoveNodeData:
    def __init__(self, move: chess.Move=None, evaluation: int=None, fullmove_number: int=None) -> None:
        self.move = move
        self.evaluation = evaluation
        self.fullmove_number = fullmove_number

    def __eq__(self, other):
        return (
            self.move == other.move and self.evaluation == other.evaluation 
            and self.fullmove_number == other.fullmove_number
        )

    def __lt__(self, other):
        return (
            self.evaluation < other.evaluation
        )

    def __gt__(self, other):
        return (
            self.evaluation > other.evaluation
        )

class MoveNode(Node):
    def __init__(self, data, children: list = None, parent=None):
        super().__init__(data, children, parent)
        self.total_weight = self.get_total_weight()

    def __str__(self) -> str:
        return f"Move number: {self.data.fullmove_number}, evaluation: {self.data.evaluation} move: {self.data.move.__str__()}"

    def __repr__(self) -> str:
        return self.__str__()

    def compare_data(self, data_1: MoveNodeData, data_2: MoveNodeData) -> int:
        if data_1.evaluation is None:
            return -1
        
        if data_2.evaluation is None:
            return 1

        if data_1.evaluation == data_2.evaluation:
            return 0
        if data_1.evaluation < data_2.evaluation:
            return -1
        if data_1.evaluation > data_2.evaluation:
            return 1

    def compare(self, other):
        if self.total_weight > other.total_weight:
            return 1
        elif self.total_weight < other.total_weight:
            return -1
        else:
            return 0

    def get_total_weight(self):
        """
        The total weight is the sum of all the weights of this 
        node's ancestors
        """
        node = self.parent
        weight = self.data.evaluation

        while node is not None:
            weight += node.data.evaluation
            node = node.parent
        
        return weight

class AIPlayer:
    def __init__(self, board: chess.Board, color: str) -> None:
        self.board = board
        self.color = color

    def get_legal_moves(self, board: chess.Board=None):
        if not board:
            board = self.board

        return list(board.legal_moves)

    def play(self, board: chess.Board=None) -> chess.Move:
        """
        Selects a move using some technique from the list of legal moves
        """
        legal_moves = self.get_legal_moves(board)
        
        return legal_moves[0]
    
    def choose_move(self, board: chess.Board=None):
        return self.play()

    def false_move(self, move: chess.Move=None, board: chess.Board=None) -> chess.Board:
        # make a copy of the board for move testing
        if not board:
            board_copy = copy.deepcopy(self.board)
        else:
            board_copy = board

        if not move:
            move = self.play(board_copy)
        
        board_copy.push(move)

        return board_copy

    def evaluate_board(self, board: chess.Board=None) -> int:
        print("Calling evaluate_board method")
        if board is None: 
            board = self.board

        regex = re.compile("\w")
        string = board.__str__()
        
        material_sum = 0

        ranks = [ row.split(' ') for row in string.split('\n') if regex.search(row)]
        
        for i, rank in enumerate(ranks):
            for j, notation in enumerate(rank):
                if regex.search(notation):
                    piece_color = Piece.get_piece_color_based_on_notation(notation)
                    material_sum += Piece.get_piece_value_from_notation_and_position(notation, piece_color, 7-i, 7-j)

        return material_sum

    def make_move(self, chess_board: ChessBoard):
        move = self.choose_move()
        chess_board._play(move=move)

    def create_moves_subtree(
        self, board: chess.Board, move, tree: Tree, 
        parent_node, current_height, required_height
    ):
        try:
            board = copy.deepcopy(board)

            board.push(move)
            evaluation = self.evaluate_board(board)

            data = MoveNodeData(move, evaluation, board.fullmove_number)

            node = MoveNode(data=data)

            tree.add_node(parent_node=parent_node, new_node=node)

            if current_height == required_height:
                return node
            
            else:
                for _move in board.legal_moves:
                    self.create_moves_subtree(
                        board, _move, tree, node, current_height+1, required_height
                    )
                
                return node

        except AssertionError as e:
            print(f"Got assetion error")
            print("The board is")
            pprint(board.__str__().split('\n'))
            print(f"The move to make is: {move}")
            breakpoint()
            raise e

    def compute_moves_tree(self, required_height=4, board: chess.Board=None):
        """
        Creates a tree of all the possible moves in the game to a certain depth with a root node that is "empty".
        The root node has no real significance in the game but is created because we wanted to instill a tree 
        data structure but at eery point in time in a game there can be multiple moes thus making it 
        difficult to select a root from them
        """
        if not board:
            # create a copy of the board so as not to affect the actual board
            board = self.board

        root_node = MoveNode(MoveNodeData()) # create a root node with evaluation 0 and move None
        
        tree = Tree(root_node=root_node)

        # create nodes of the legal moves and the board evaluation
        for move in board.legal_moves:
            self.create_moves_subtree(
                board=board, move=move, tree=tree, parent_node=root_node, current_height=0,
                required_height=required_height
            )

        return tree

class RandomPlayer(AIPlayer):
    def play(self) -> chess.Move:
        legal_moves = list(self.board.legal_moves)

        move = random.choice(legal_moves)

        return move

class PlayerWithEvaluation(AIPlayer):
    def play(self) -> chess.Move:
        return super().play()
    
    def choose_move(self, board: chess.Board=None):
        legal_moves = self.get_legal_moves()
        
        random.shuffle(legal_moves)

        chosen_move = None

        for move in legal_moves:
            evaluation_before = self.evaluate_board()
            fake_board = self.false_move(move)
            evaluation_after = self.evaluate_board(fake_board)

            if chosen_move is None:
                chosen_move = move
            else:
                # if the player is white and the move results in a higher material for white
                if evaluation_after > evaluation_before and self.color == "w":
                    chosen_move = move
                # if the player is black and the move results in higher material for black
                elif evaluation_before > evaluation_after and self.color == "b":
                    chosen_move = move
        
        return chosen_move


class MiniMaxPlayer(PlayerWithEvaluation):
    def __init__(self, board: chess.Board, color: str) -> None:
        super().__init__(board, color)
        self.moves_tree: Tree = None
        self.last_move_node: MoveNode = None

    def minimax(self, node: MoveNode, is_max=None):
        """
        The next move in the game is the node's children not the node itself.
        So evaluation starts from the children of the node.
        This is done so because in computing the game tree, the first node is always an "empty" node 
        thus it has no real meaning in the game
        """
        if is_max is None:
            is_max = self.color == 'w'

        if len(node.children) > 0:
            if is_max:
                return max( [ self.minimax(child, not is_max) for child in node.children ] )
            else:
                return min( [ self.minimax(child, not is_max) for child in node.children ] )
        else:
            return node

    def expand_subtree_to_depth(self, root_node: MoveNode, depth=3, revise_existing_children=False, board: chess.Board=None) -> Tree:
        """
        Depth here does not include the root node, just its descendants.
        The board's latest move must correspond to the root_node's move for this method to work effectively
        """
        if board is None:
            board = self.board

        tree = Tree(root_node=root_node)

        current_depth = tree.get_height() - 1

        leaf_nodes = tree.get_leaf_nodes()
        
        print(f"The tree's root nodes are: ")
        print(leaf_nodes)

        for index, node in enumerate(leaf_nodes):
            print(f"On node: {index+1} of the tree's leaf nodes. The node: ")
            print(node)
            _dummy_board = copy.deepcopy(board)
            # since we are getting the leaf moves, we have to first of all execute all of the 
            # moves preceding those ones in the tree
            _node = node.parent
            
            moves_to_make = []

            while _node is not root_node:
                moves_to_make.append(_node)

                _node = _node.parent

                if _node is None:
                    break
            
            print("This node's parents are: ")
            print(moves_to_make)

            while moves_to_make:
                move = moves_to_make.pop()
                print(f"Executing the move node: {move}")
                _dummy_board.push(move.data.move)

            try:
                print("Creating subtree for this leaf node")
                self.create_moves_subtree(
                    _dummy_board, node.data.move, tree, 
                    root_node, current_depth, depth
                )
            except Exception as e:
                raise e
        
        return tree

    def choose_move(self, board: chess.Board = None):
        if board is None:
            board = self.board

        if self.last_move_node:
            grandparent = self.last_move_node.parent

            # check where in the tree the last move is found and deepen the tree from there 
            # instead of creating a new tree
            new_root_node = None
            
            last_move = board.move_stack.pop()

            # for parent in grandparent.children:
            #     last_move_node_found = False
            #     for child in parent.children:
            #         if child.data.move == last_move and child.data.fullmove_number == board.fullmove_number:
            #             new_root_node = child
            #             last_move_node_found = True
                
            #     if last_move_node_found:
            #         break
            
            # last_move_node_found = False
            for child in self.last_move_node.children:
                if child.data.move == last_move and child.data.fullmove_number == board.fullmove_number:
                    new_root_node = child
                    # last_move_node_found = True
                    break

            tree = self.expand_subtree_to_depth(new_root_node)
        
        else:
            # compute the game tree and get the leaf with the smallest or largest 
            # evaluation depending on the player's color
            print("Computing the moves tree")
            tree = self.compute_moves_tree(required_height=2, board=board)
        
        # print("Selecting the optimal move using minimax")
        optimal_node = self.minimax(tree.root_node)

        node = optimal_node.parent if optimal_node.parent is not None else node
        # print("The weight along this optimal node's path is")
        # print(optimal_node.total_weight)

        # get the predecessor of the optimal node that is a direct descendant of the root node
        while node.parent is not tree.root_node and node.parent is not None:
            node = node.parent

        self.last_move_node = node

        return node.data.move

    def play(self) -> chess.Move:
        return super().play()