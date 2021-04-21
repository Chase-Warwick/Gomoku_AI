import math
from board_util import GoBoardUtil, BLACK, WHITE, PASS

PASS = "pass"

def uct_val(node, child, exploration, max_flag):
    """
    Returns score based on the child nodes contributions
    to winning games and the amount of uncertainty about
    said child node

    @Params:
        node
            TreeNode object
        child
            TreeNode object representing the node being evaluated
        exploration
            Number representing a constant used to determine
            how much the algorithm should prioritise nodes
            which have a small set of samples
        max_flag
            Integer object representing the color of the
            current player
    @Returns
        Number representing how much this node should be
        prioritised over other nodes for future simulations
    """
    if child.get_visits() == 0:
        return float("inf")
    else:
        return float(child.get_blackWins()) / child.get_visits() + exploration * math.sqrt(
            math.log(node.get_visits()) / child.get_visits()
        )

def play_game(board, color, limit):
    """
    Run a simulation game according to given parameters
    """
    nuPasses = 0
    for i in range(limit):
        color = board.current_player
        move = GoBoardUtil.generate_random_move(board, color, True)
        if move == None:
            nuPasses += 1
        else:
            board.play_move_gomoku(move, color)
            nuPasses = 0
        if nuPasses > 1:
            break
    return board.winner()


class TreeNode(object):
    """
    MCTS Tree Node
    """
    def __init__(self, parent):
        """
        Creates an instance of TreeNode object

        TreeNode object is created on the expansion of other
        TreeNode objects

        @Params
            parent
                TreeNode object representing the TreeNode
                which was expanded resulting in the creation
                of the new TreeNode object (self) being
                instantiated
        """
        self.parent = parent
        self.children = {}
        self.visits = 0
        self.blackWins = 0
        self.expanded = False
        self.move = None
    
    def expand(self, board, color):
        """
        Expands tree by creating new children

        @Params
            board
                simple_board object representing 
                the current gamestate
            color
                Integer object representing the
                current player
        """
        moves = board.get_empty_points()
        for move in moves:
            if move not in self.children:
                if board.is_legal_gomoku(move, color):
                    self.children[move] = TreeNode(self)
                    self.children[move].set_move(move)
        self.expanded = True
    
    def select(self, exploration, max_flag):
        """
        Returns the node which has a high value or high level
        of uncertainty about it's value or some combination
        therein

        @Params
            exploration
                Constant representing how much the algorithm
                should value exploration
            max_flag
                Integer object representing the color of the
                current player
        """
        return max(
            self.children.items(),
            key=lambda items: uct_val(self, items[1], exploration, max_flag),
        )
    
    def update(self, leaf_value):
        """
        Update node values from leaf evaluation

        @Params
            leaf_value
                Value representing the outcome of
                choosing this leaf node
        """
        self.blackWins += leaf_value
        self.visits += 1
    
    def update_recursive(self, leaf_value):
        """
        Update node and all of it's parents using leaf
        evaluation

        @Params
            leaf_value
                Value representing the outcome of
                choosing this leaf node
        """
        if self.parent:
            self.parent.update_recursive(leaf_value)
        self.update(leaf_value)
    
    def is_leaf(self):
        """
        Check if a given TreeNode is a leaf node

        @Returns
            Boolean object representing whether a given
            TreeNode is a leaf node of the graph
        """
        return self.children == {}
    
    def is_root(self):
        """
        Check if a given TreeNode is the root node

        @Returns
            Boolean object representing whether a given
            TreeNode is the root of the graph
        """
        return self.parent is None

    def set_parent(self, parent):
        self.parent = parent
    
    def get_parent(self):
        return self.parent
    
    def get_children(self):
        return self.children
    
    def get_visits(self):
        return self.visits
    
    def get_blackWins(self):
        return self.blackWins
    
    def get_expanded_boolean(self):
        return self.expanded

    def set_move(self, move):
        self.move = move
    
    def get_move(self):
        return self.move

class MCTS(object):
    def __init__(self):
        self.root = TreeNode(None)
        self.toPlay = BLACK
    
    def playout(self, board, color):
        node = self.root
        if not node.get_expanded_boolean():
            node.expand(board, color)
        while not node.is_leaf():
            max_flag = color == BLACK
            move, next_node = node.select(self.exploration, max_flag)
            if not board.is_legal(move, color):
                print("Why here")
            if move != PASS:
                move = None
            board.play_move(move, color)
            color = GoBoardUtil.opponent(color)
            node = next_node
        assert node.is_leaf()
        if not node.get_expanded_boolean():
            node.expand(board, color) 
        
        assert board.current_player == color
        leaf_value = self.evaluate_rollout(board, color)
        node.update_recursive(leaf_value)
    
    def evaluate_rollout(self, board, toPlay):
        winner = play_game(
            board,
            toPlay,
            self.limit
        )
        if winner == BLACK:
            return 1
        else:
            return 0
    
    def get_move(
        self,
        board,
        toPlay,
        limit,
        exploration,
        numSimulation
    ):
        """
        Runs many simulations before returning a guess for
        which move is best
        """
        if self.toPlay != toPlay:
            self.root = TreeNode(None)
        self.toPlay = toPlay
        self.limit = limit
        self.exploration = exploration
        
        for n in range(numSimulation):
            boardCopy = board.copy()
            self.playout(boardCopy, toPlay)
        moveList = [
            (move, node.get_visits()) for move, node in self.root.children.items()
        ]
        if not moveList:
            return None
        moveList = sorted(moveList, key=lambda i: i[1], reverse=True)
        move = moveList[0]
        if move[0] == PASS:
            return None
        assert board.is_legal(move[0], toPlay)
        return move[0]
    
    def update_with_move(self, lastMove):
        """
        Step forward in the tree, keeping everything we already know about the subtree, assuming
        that get_move() has been called already. Siblings of the new root will be garbage-collected.
        """
        if lastMove in self.root.get_children():
            self.root = self.root.get_children()[lastMove]
        else:
            self.root = TreeNode(None)
        self.root.set_parent(None)
        self.toPlay = GoBoardUtil.opponent(self.toPlay)
    
    def get_root(self):
        return self.root






    
