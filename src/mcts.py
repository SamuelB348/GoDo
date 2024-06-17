"""
This section implements the logic behind MCTS.

Freely inspired and adapted from: https://ai-boson.github.io/mcts/
"""

from __future__ import annotations

import time
import random
from typing import Optional, Sequence
import numpy as np

from gamestate import GameState
from types_constants import *


def argmax(seq: Sequence[float]):
    """
    Compute the argmax of a sequence of floats.

    :param seq: a sequence of floats
    :return: the argmax of that sequence
    """

    return max(range(len(seq)), key=seq.__getitem__)


class MonteCarloTreeSearchNode:
    """
    Class containing all the attributes and logic to run the 4 phases of MCTS:
    - Selection
    - Expansion
    - Simulation
    - Backpropagation
    """

    # A cache containing the hash of the previously seen positions, and the associated gain.
    # Key is a hash, value is a list [nb_visits, nb_victories]
    STATE_CACHE: dict[int, list[int]] = {}

    def __init__(
        self,
        state: GameState,
        player: Player,
        c_param: float,
        improved_playouts: bool,
        parent: Optional[MonteCarloTreeSearchNode] = None,
        parent_action: Optional[Action] = None,
    ):
        # GameState encapsulating the game logic
        self.state: GameState = state

        # The parent node if it exists
        self.parent: Optional[MonteCarloTreeSearchNode] = parent
        # The parent action that led to this node
        self.parent_action: Optional[Action] = parent_action

        # The list of the explored children (starting empty)
        self.children: list[MonteCarloTreeSearchNode] = []
        # The number of visits
        self.N: int = 0
        # The number of victories
        self.Q: int = 0

        # The list of the actions to explore if the tree is not fully expanded
        self.untried_actions: Union[list[ActionDodo], list[ActionGopher]] = self.initialize_actions()

        # The player we're playing for during all the game
        self.player: Player = player
        # The opponent for all the game
        self.opponent: Player = R if self.player == B else B

        # The C exploration parameter in the UCT formula
        self.c_param: float = c_param
        # The boolean indicating if we improve the playouts with minmax or not
        self.improved_playouts: bool = improved_playouts

    def initialize_actions(self) -> Union[list[ActionDodo], list[ActionGopher]]:
        """
        Returns the untried actions when a node is created (i.e. the legals actions from this node)

        :return: a list of legal actions
        """

        untried_actions: Union[list[ActionDodo], list[ActionGopher]] = (
            self.state.get_legal_actions().copy()
        )
        # Shuffle the legals, so we don't introduce a deterministic bias
        random.shuffle(untried_actions)

        return untried_actions

    def expand(self) -> MonteCarloTreeSearchNode:
        """
        Expands the current node by creating a new node representing one of its child.

        :return: a new MonteCarloTreeSearchNode instance
        """

        action: Action = self.untried_actions.pop()
        next_state: GameState = self.state.move(action)

        child_node: MonteCarloTreeSearchNode = MonteCarloTreeSearchNode(
            next_state,
            self.player,
            self.c_param,
            self.improved_playouts,
            parent=self,
            parent_action=action,
        )
        self.children.append(child_node)

        return child_node

    def is_terminal_node(self) -> bool:
        """
        Returns True if this node represents a final situation (someone has won).

        :return: a boolean saying it node is terminal or not
        """

        return self.state.is_game_over()

    def rollout(self) -> tuple[int, int, int]:
        """
        Executes a rollout from this node, i.e. a simulation. Based on the result of the game,
        it returns 1 (victory) or 0 (defeat).
        It also updates the STATE_CACHE class attribute appropriately.

        :return: a tuple (total_reward, total_visits, game_length_of_rollout)
        """

        current_rollout_state: GameState = self.state
        result, game_length = current_rollout_state.simulate_game(
            self.improved_playouts
        )

        if (
            result != self.state.turn
        ):  # Reward for the player who has played, not the one who must play
            reward: int = 1
        else:
            reward = 0

        # We add up the result of the simulation and the previous results of the transposition table
        # of the current position. These previous results are contained in the STATE_CACHE
        if self.state.hash in MonteCarloTreeSearchNode.STATE_CACHE:
            additional_visits: int = MonteCarloTreeSearchNode.STATE_CACHE[
                self.state.hash
            ][0]
            additional_result: int = MonteCarloTreeSearchNode.STATE_CACHE[
                self.state.hash
            ][1]
            MonteCarloTreeSearchNode.STATE_CACHE[self.state.hash][0] += 1
            MonteCarloTreeSearchNode.STATE_CACHE[self.state.hash][1] += reward
        else:
            additional_visits = 0
            additional_result = 0
            MonteCarloTreeSearchNode.STATE_CACHE[self.state.hash] = [1, reward]

        return reward + additional_result, 1 + additional_visits, game_length

    def backpropagate(self, reward: int, visits: int) -> None:
        """
        Backpropagation of the reward to the current node and its ancestors.

        :param reward: the reward returned from a rollout
        :param visits: the number of visits returned from a rollout
        :return: None
        """

        self.N += visits
        self.Q += reward
        # If the node is not the root, we backpropagate to its parent
        if self.parent is not None:
            # Be careful here, my victories are my parent's defeats, that's why we do visits-reward
            self.parent.backpropagate(visits - reward, visits)

    def is_fully_expanded(self) -> bool:
        """
        Returns true if there are no remaining actions to explore from this node.

        :return: a boolean
        """

        return len(self.untried_actions) == 0

    def best_child(self) -> MonteCarloTreeSearchNode:
        """
        Returns the best child to select based on the UCT formula.

        :return: a child node of the current node
        """

        uct_choice: list[float] = [
            (c.Q / c.N) + self.c_param * np.sqrt((2 * np.log(self.N) / c.N))
            for c in self.children
        ]

        return self.children[argmax(uct_choice)]

    def best_final_child(self) -> MonteCarloTreeSearchNode:
        """
        Returns the best child to select when we must retrieve an action to the referee.
        Here we chose the most visited children.

        :return: a child node of the current node
        """

        choices_weight: list[int] = [c.N for c in self.children]
        return self.children[np.argmax(choices_weight)]

    def _tree_policy(self) -> MonteCarloTreeSearchNode:
        """
        Defines the tree policy to select the next node to explore.
        Here it's very classical, if a node is not fully expanded we expand it,
        otherwise we go down the tree according to UCT.

        :return: a node to perform a rollout from
        """

        current_node: MonteCarloTreeSearchNode = self
        while not current_node.is_terminal_node():

            if not current_node.is_fully_expanded():
                return current_node.expand()

            current_node = current_node.best_child()

        return current_node

    def perform_iterations(self, allocated_time: float) -> float:
        """
        Perform a certain number of iterations on the current node.
        This number depends on the allocated time to make a move.

        :param allocated_time: time allocated to select an action
        :return: Nothing except the mean game length over all the rollouts
        """

        length_count: int = 0
        simulation_count: int = 1
        start_time: float = time.time()

        while time.time() - start_time < allocated_time:
            v: MonteCarloTreeSearchNode = self._tree_policy()
            reward, visits, game_length = v.rollout()
            v.backpropagate(reward, visits)

            length_count += game_length
            simulation_count += 1

            # Here we manage the time as follows:
            # If after 200 simulations the gap between the number of visits of the most visited node
            # and the number of visits of the second most visited can't be filled in the remaining
            # time (it's an estimation), then we can safely stop and save time
            if simulation_count % 200 == 0:
                first_visited, second_visited = self.get_two_most_visited()
                time_spent = time.time() - start_time
                time_left = allocated_time - time_spent
                if (
                    simulation_count * (time_left / time_spent)
                    < first_visited - second_visited
                ):
                    break
                # In the same manner, if the temporary best final child has more than 100 visits
                # and its winning rate is very close to 1, we can safely stop
                if (
                    first_visited > 100
                    and self.best_final_child().Q / first_visited > 0.98
                ):
                    break

        print(simulation_count)
        # Here, to avoid any problem we set the minimum game length to return to 4,
        return max(int(length_count / simulation_count), 4)

    def get_two_most_visited(self) -> tuple[float, float]:
        """
        Returns the number of visits of the tw most visited nodes in the tree.

        :return: a tuple (# visits 1st most visited child, # visits 2nd most visited child)
        """

        first_max = second_max = float("-inf")

        for child in self.children:
            if child.N > first_max:
                second_max = first_max
                first_max = child.N
            elif child.N > second_max:
                second_max = child.N

        return first_max, second_max

    def __str__(self):
        assert self.N > 0
        return (
            f"Parent action : {self.parent_action}\n"
            f"|-- Number simulations : {self.N}\n"
            f"|-- Number of victories : {self.Q}\n"
            f"|-- Ratio : {self.Q/self.N:.3f}"
        )
