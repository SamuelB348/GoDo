from __future__ import annotations

import copy
import time
from typing import Optional
import numpy as np

from dodo import *
from gopher import *


def argmax(seq):
    return max(range(len(seq)), key=seq.__getitem__)


class MonteCarloTreeSearchNode:
    STATE_CACHE = {}

    def __init__(
        self,
        state,
        player: Player,
        c: float,
        p: float,
        parent=None,
        parent_action: Optional[Action] = None,
    ):
        self.state = state
        self.parent: Optional[MonteCarloTreeSearchNode] = parent
        self.parent_action: Optional[Action] = parent_action

        self.children: list[MonteCarloTreeSearchNode] = []
        self.N = 0
        self.Q = 0

        self.untried_actions: list[ActionDodo] = self.initialize_actions()

        self.player: Player = player
        self.opponent: Player = R if self.player == B else B

        self.c = c
        self.p = p

    def initialize_actions(self) -> list[ActionDodo]:
        self.untried_actions = self.state.get_legal_actions().copy()
        random.shuffle(self.untried_actions)
        return self.untried_actions

    def expand(self) -> MonteCarloTreeSearchNode:
        action: ActionDodo = self.untried_actions.pop()
        next_state = self.state.move(action)
        child_node: MonteCarloTreeSearchNode = MonteCarloTreeSearchNode(
            next_state, self.player, self.c, self.p, parent=self, parent_action=action
        )
        self.children.append(child_node)

        return child_node

    def is_terminal_node(self) -> bool:
        return self.state.is_game_over()

    def rollout(self) -> tuple[int, int, int]:
        current_rollout_state: GameStateDodo = self.state
        result, game_length = current_rollout_state.simulate_game(self.p)

        if result != self.state.turn:  # Reward for the player who has played, not the one who must play
            if self.state.hash in MonteCarloTreeSearchNode.STATE_CACHE:
                additional_visits = MonteCarloTreeSearchNode.STATE_CACHE[self.state.hash][0]
                additional_result = MonteCarloTreeSearchNode.STATE_CACHE[self.state.hash][1]
                MonteCarloTreeSearchNode.STATE_CACHE[self.state.hash][0] += 1
                MonteCarloTreeSearchNode.STATE_CACHE[self.state.hash][1] += 1
            else:
                additional_visits = 0
                additional_result = 0
                MonteCarloTreeSearchNode.STATE_CACHE[self.state.hash] = [1, 1]
            return 1 + additional_result, 1 + additional_visits, game_length
        if self.state.hash in MonteCarloTreeSearchNode.STATE_CACHE:
            additional_visits = MonteCarloTreeSearchNode.STATE_CACHE[self.state.hash][0]
            additional_result = MonteCarloTreeSearchNode.STATE_CACHE[self.state.hash][1]
            MonteCarloTreeSearchNode.STATE_CACHE[self.state.hash][0] += 1
            MonteCarloTreeSearchNode.STATE_CACHE[self.state.hash][1] += 0
        else:
            additional_visits = 0
            additional_result = 0
            MonteCarloTreeSearchNode.STATE_CACHE[self.state.hash] = [1, 0]
        return 0 + additional_result, 1 + additional_visits, game_length

    def backpropagate(self, reward, visits) -> None:
        self.N += visits
        self.Q += reward
        if self.parent is not None:
            self.parent.backpropagate(visits - reward, visits)

    def is_fully_expanded(self) -> bool:
        return len(self.untried_actions) == 0

    def best_child(self, c_param=0.1) -> MonteCarloTreeSearchNode:
        uct_choice = [
            (c.Q / c.N) + c_param * np.sqrt((2 * np.log(self.N) / c.N))
            for c in self.children
        ]

        return self.children[argmax(uct_choice)]

    def best_final_child(self) -> MonteCarloTreeSearchNode:
        choices_weight: list[int] = [c.N for c in self.children]
        return self.children[np.argmax(choices_weight)]

    @staticmethod
    def rollout_policy(possible_moves) -> ActionDodo:
        return random.choice(possible_moves)

    def _tree_policy(self) -> MonteCarloTreeSearchNode:
        current_node = self
        while not current_node.is_terminal_node():

            if not current_node.is_fully_expanded():
                return current_node.expand()

            current_node = current_node.best_child(c_param=self.c)

        return current_node

    def best_action(
        self, allocated_time: float
    ) -> tuple[MonteCarloTreeSearchNode, int | None]:
        if self.is_fully_expanded() and len(self.children) == 1:
            return self.best_final_child(), None

        length_count: int = 0
        simulation_count: int = 1
        start_time: float = time.time()

        while time.time() - start_time < allocated_time:
            v: MonteCarloTreeSearchNode = self._tree_policy()
            reward, visits, game_length = v.rollout()
            v.backpropagate(reward, visits)
            length_count += game_length
            simulation_count += 1

            if simulation_count % 200 == 0:
                first_visited, second_visited = self.get_two_most_visited()
                time_spent = time.time() - start_time
                time_left = allocated_time - time_spent
                if simulation_count * (time_left/time_spent) < first_visited - second_visited:
                    break
                if first_visited > 100 and self.best_final_child().Q / first_visited > 0.98:
                    break

        print(simulation_count)
        return self.best_final_child(), max(int(length_count / simulation_count), 4)

    def get_two_most_visited(self):
        first_max = second_max = float('-inf')

        for child in self.children:
            if child.N > first_max:
                second_max = first_max
                first_max = child.N
            elif child.N > second_max:
                second_max = child.N

        return first_max, second_max

    def __str__(self):
        return (
            f"Parent action : {self.parent_action}\n"
            f"|-- Number simulations : {self.N}\n"
            f"|-- Number of victories : {self.Q}\n"
            f"|-- Ratio : {self.Q/self.N:.3f}"
        )
