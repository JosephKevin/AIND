"""Finish all TODO items in this file to complete the isolation project, then
test your agent's strength against a set of known agents using tournament.py
and include the results in your report.
"""
import random
from sklearn.neighbors import DistanceMetric
MANHATTAN_DIST = DistanceMetric.get_metric('manhattan')
MINKOWSKI_DIST = DistanceMetric.get_metric('minkowski')
CHEBYSHEV_DIST = DistanceMetric.get_metric('chebyshev')


class SearchTimeout(Exception):
    """Subclass base exception for code clarity. """
    pass


def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    This should be the best heuristic function for your project submission.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    #minkowski distance to the center
    y, x = game.get_player_location(player)
    w, h = game.width / 2., game.height / 2.
    return(CHEBYSHEV_DIST.pairwise([(x,y), (w,h)])[0][1])
    
    
def custom_score_2(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    return float(own_moves - (2 * opp_moves))


def custom_score_3(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.
    This is an aggressive version of my moves - opponent moves as suggested in 
    class.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")
    #minkowski distance to the center
    y, x = game.get_player_location(player)
    w, h = game.width / 2., game.height / 2.
    return(MINKOWSKI_DIST.pairwise([(x,y), (w,h)])[0][1])


class IsolationPlayer:
    """Base class for minimax and alphabeta agents -- this class is never
    constructed or tested directly.

    ********************  DO NOT MODIFY THIS CLASS  ********************

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """
    def __init__(self, search_depth=3, score_fn=custom_score, timeout=10.):
        self.search_depth = search_depth
        self.score = score_fn
        self.time_left = None
        self.TIMER_THRESHOLD = timeout


class MinimaxPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using depth-limited minimax
    search. You must finish and test this player to make sure it properly uses
    minimax to return a good move before the search time limit expires.
    """

    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        **************  YOU DO NOT NEED TO MODIFY THIS FUNCTION  *************

        For fixed-depth search, this function simply wraps the call to the
        minimax method, but this method provides a common interface for all
        Isolation agents, and you will replace it in the AlphaBetaPlayer with
        iterative deepening search.

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left

        # Initialize the best move so that this function returns something
        # in case the search fails due to timeout
        best_move = (-1, -1)

        try:
            # The try/except block will automatically catch the exception
            # raised when the timer is about to expire.
            return self.minimax(game, self.search_depth)

        except SearchTimeout:
            pass  # Handle any actions required after timeout as needed

        # Return the best move from the last completed search iteration
        return best_move

    def minimax(self, game, depth):
        """Implement depth-limited minimax search algorithm as described in
        the lectures.

        This should be a modified version of MINIMAX-DECISION in the AIMA text.
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Minimax-Decision.md

        **********************************************************************
            You MAY add additional methods to this class, or define helper
                 functions to implement the required functionality.
        **********************************************************************

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project tests; you cannot call any other evaluation
                function directly.

            (2) If you use any helper functions (e.g., as shown in the AIMA
                pseudocode) then you must copy the timer check into the top of
                each helper function or else your agent will timeout during
                testing.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        # get the list of possible legal moves for the active player in 
        # the current state.
        available_moves = game.get_legal_moves()
        if len(available_moves) == 0 or depth == 0:
            return (-1, -1)
        maximizing_move = (-1, -1)
        for move in available_moves:    
            maximizing_move = move
            break
        # among each available move select the move that provides the largest
        # value.
        score = float("-inf")
        for move in available_moves:
            curr_scr = self.min_value(game.forecast_move(move), depth-1)
            if curr_scr >= score:
                score = curr_scr
                maximizing_move = move
        return maximizing_move

    def min_value(self, game, depth):
        """
        Function to find the min value among all the possible 
        1ply actions

        Params:
            1. game: isolation.Board
                An instance of the Isolation game `Board` class representing the
                current game state.
            2. depth: integer value to keep track of the depth.

        Returns:
            1. score: the current score of the game board from the perspective
                    of the active player.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        # check if its the end game and or depth is 0
        available_moves = game.get_legal_moves()
        if len(available_moves) == 0 or depth == 0:
            return self.score(game, self)
        min_score = float("inf")
        for move in available_moves:
            curr_score = self.max_value(game.forecast_move(move), depth-1)
            if curr_score < min_score:
                min_score = curr_score
        return min_score

    def max_value(self, game, depth):
        """
        Function to find the max value among all the possible 
        1ply actions

        Params:
            1. game: isolation.Board
                An instance of the Isolation game `Board` class representing the
                current game state.
            2. depth: integer value to keep track of the depth.

        Returns:
            1. score: the current score of the game board from the perspective
                    of the active player.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        # check if its the end game and or depth is 0
        available_moves = game.get_legal_moves()
        if len(available_moves) == 0 or depth == 0:
            return self.score(game, self)
        max_score = float("-inf")
        for move in available_moves:
            curr_score = self.min_value(game.forecast_move(move), depth-1)
            if curr_score > max_score:
                max_score = curr_score
        return max_score

class AlphaBetaPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using iterative deepening minimax
    search with alpha-beta pruning. You must finish and test this player to
    make sure it returns a good move before the search time limit expires.
    """

    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        Modify the get_move() method from the MinimaxPlayer class to implement
        iterative deepening search instead of fixed-depth search.

        **********************************************************************
        NOTE: If time_left() < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left
        # Initialize the best move so that this function returns something
        # in case the search fails due to timeout
        available_moves = game.get_legal_moves()
        best_move = (-1, -1)
        for move in available_moves:    
            best_move = move
            break
        
        try:
            # The try/except block will automatically catch the exception
            # raised when the timer is about to expire.
            depth = 0
            while 1:
                best_move = self.alphabeta(game, depth)
                depth += 1

        except SearchTimeout:
            pass
        return best_move

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf")):
        """Implement depth-limited minimax search with alpha-beta pruning as
        described in the lectures.

        This should be a modified version of ALPHA-BETA-SEARCH in the AIMA text
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Alpha-Beta-Search.md

        **********************************************************************
            You MAY add additional methods to this class, or define helper
                 functions to implement the required functionality.
        **********************************************************************

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project tests; you cannot call any other evaluation
                function directly.

            (2) If you use any helper functions (e.g., as shown in the AIMA
                pseudocode) then you must copy the timer check into the top of
                each helper function or else your agent will timeout during
                testing.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        # get the list of possible legal moves for the active player in 
        # the current state.
        available_moves = game.get_legal_moves()
        if len(available_moves) == 0 or depth == 0:
            return (-1, -1)
        max_score = float("-inf")
        maximizing_move = (-1, -1)
        for move in available_moves:    
            maximizing_move = move
            break
        for move in available_moves:
            curr_score = self.min_value(game.forecast_move(move), depth-1, alpha, beta)
            if curr_score > max_score:
                max_score = curr_score
                maximizing_move = move
            if max_score >= beta:
                return maximizing_move
            alpha = max(max_score, alpha)
        return maximizing_move

    def max_value(self, game, depth, alpha, beta):
        """
        Function to find max values among all the possible 
        1ply actions

        Params:
            game : isolation.Board
                An instance of the Isolation game `Board` class representing the
                current game state

            depth : int
                Depth is an integer representing the maximum number of plies to
                search in the game tree before aborting

            alpha : float
                Alpha limits the lower bound of search on minimizing layers

            beta : float
                Beta limits the upper bound of search on maximizing layers

        Returns:
            v: the max value among all possible 1ply actions.
            actionL the action that provided the maximum value among all 1ply actions.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        # check if its the end game and or depth is 0
        available_moves = game.get_legal_moves()
        if len(available_moves) == 0 or depth == 0:
            return self.score(game, self)
        max_score = float("-inf")
        for move in available_moves:
            curr_score = self.min_value(game.forecast_move(move), depth-1, alpha, beta)
            if curr_score > max_score:
                max_score = curr_score
            if max_score >= beta:
                return max_score
            alpha = max(max_score, alpha)
        return max_score

    def min_value(self, game, depth, alpha, beta):
        """
        Function to find min values among all the possible 
        1ply actions

        Params:
            game : isolation.Board
                An instance of the Isolation game `Board` class representing the
                current game state

            depth : int
                Depth is an integer representing the maximum number of plies to
                search in the game tree before aborting

            alpha : float
                Alpha limits the lower bound of search on minimizing layers

            beta : float
                Beta limits the upper bound of search on maximizing layers

        Returns:
            v: the min value among all possible 1ply actions.
            actionL the action that provided the minimum value among all 1ply actions.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        # check if its the end game and or depth is 0
        available_moves = game.get_legal_moves()
        if len(available_moves) == 0 or depth == 0:
            return self.score(game, self)
        min_score = float("inf")
        for move in available_moves:
            curr_score = self.max_value(game.forecast_move(move), depth-1, alpha, beta)
            if curr_score < min_score:
                min_score = curr_score
            if min_score <= alpha:
                return min_score
            beta = min(min_score, beta)
        return min_score

        
        