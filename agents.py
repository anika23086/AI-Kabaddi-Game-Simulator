import random
import itertools
import math
import time
from game_environment import KabaddiGame

class Agent:
    def __init__(self, team):
        if team not in ['A', 'B']:
            raise ValueError("Team must be 'A' or 'B'")
        self.team = team

    def select_moves(self, game: KabaddiGame):
        raise NotImplementedError

class RandomAgent(Agent):
    def select_moves(self, game: KabaddiGame):
        moves = {}
        active_players = [p for p in game.state.players.values() if p.team == self.team and not p.is_captured]
        for player in active_players:
            valid_moves = game.get_valid_moves(player.id)
            if valid_moves:
                moves[player.id] = random.choice(valid_moves)
        return moves

class GreedyAgent(Agent):
    def _manhattan_distance(self, pos1, pos2):
        if not pos1 or not pos2: return float('inf')
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def evaluate_state(self, game: KabaddiGame):
        score = 0
        my_players = [p for p in game.state.players.values() if p.team == self.team]
        opponent_team = 'B' if self.team == 'A' else 'A'
        opponent_players = [p for p in game.state.players.values() if p.team == opponent_team]
        my_gold_pos = game.state.gold_pos.get(self.team)
        opponent_gold_pos = game.state.gold_pos.get(opponent_team)
        winner = game.check_terminal_state()
        if winner == self.team: return float('inf')
        if winner == opponent_team: return float('-inf')
        for player in my_players:
            if player.is_captured:
                score -= 1000
                continue
            if player.has_gold:
                score += 500
                my_home_territory_edge = game.state.half_way_x - 1 if self.team == 'A' else game.state.half_way_x
                dist_to_home = abs(player.pos[0] - my_home_territory_edge)
                score -= dist_to_home * 10
            elif opponent_gold_pos:
                dist_to_gold = self._manhattan_distance(player.pos, opponent_gold_pos)
                score -= dist_to_gold * 5
            if my_gold_pos:
                for opp in opponent_players:
                    if not opp.is_captured:
                        dist_to_our_gold = self._manhattan_distance(opp.pos, my_gold_pos)
                        score += dist_to_our_gold
            if game.state.is_in_enemy_territory(player):
                for opp in opponent_players:
                    if not opp.is_captured:
                        dist_to_opp = self._manhattan_distance(player.pos, opp.pos)
                        if dist_to_opp < 3:
                            score -= (50 / (dist_to_opp + 1))
        return score

    def select_moves(self, game: KabaddiGame):
        best_move_combination = {}
        best_score = float('-inf')
        active_players = [p for p in game.state.players.values() if p.team == self.team and not p.is_captured]
        if not active_players: return {}
        player_moves_options = [game.get_valid_moves(p.id) for p in active_players]
        move_combinations = list(itertools.product(*player_moves_options))
        if not move_combinations: return {}
        best_move_combination = {p.id: move for p, move in zip(active_players, move_combinations[0])}
        for combination in move_combinations:
            temp_game = game.clone()
            current_moves = {p.id: move for p, move in zip(active_players, combination)}
            temp_game.apply_moves(current_moves)
            score = self.evaluate_state(temp_game)
            if score > best_score:
                best_score = score
                best_move_combination = current_moves
        return best_move_combination

class AlphaBetaAgent(GreedyAgent):
    def __init__(self, team, depth=2):
        super().__init__(team)
        self.depth = depth

    def select_moves(self, game: KabaddiGame):
        return self._alphabeta_search(game)

    def _alphabeta_search(self, game: KabaddiGame):
        best_move_combination = {}
        best_score = float('-inf')
        active_players = [p for p in game.state.players.values() if p.team == self.team and not p.is_captured]
        if not active_players: return {}
        player_moves_options = [game.get_valid_moves(p.id) for p in active_players]
        move_combinations = list(itertools.product(*player_moves_options))
        if not move_combinations: return {}
        best_move_combination = {p.id: move for p, move in zip(active_players, random.choice(move_combinations))}
        alpha = float('-inf')
        beta = float('inf')
        for combination in move_combinations:
            temp_game = game.clone()
            current_moves = {p.id: move for p, move in zip(active_players, combination)}
            temp_game.apply_moves(current_moves)
            score = self._min_value(temp_game, self.depth - 1, alpha, beta)
            if score > best_score:
                best_score = score
                best_move_combination = current_moves
            alpha = max(alpha, best_score)
        return best_move_combination

    def _min_value(self, game, depth, alpha, beta):
        if depth == 0 or game.check_terminal_state() is not None:
            return self.evaluate_state(game)
        value = float('inf')
        opponent_team = 'B' if self.team == 'A' else 'A'
        active_players = [p for p in game.state.players.values() if p.team == opponent_team and not p.is_captured]
        if not active_players: return self.evaluate_state(game)
        player_moves_options = [game.get_valid_moves(p.id) for p in active_players]
        move_combinations = list(itertools.product(*player_moves_options))
        for combination in move_combinations:
            temp_game = game.clone()
            current_moves = {p.id: move for p, move in zip(active_players, combination)}
            temp_game.apply_moves(current_moves)
            value = min(value, self._max_value(temp_game, depth - 1, alpha, beta))
            if value <= alpha: return value # Prune
            beta = min(beta, value)
        return value

    def _max_value(self, game, depth, alpha, beta):
        if depth == 0 or game.check_terminal_state() is not None:
            return self.evaluate_state(game)
        value = float('-inf')
        active_players = [p for p in game.state.players.values() if p.team == self.team and not p.is_captured]
        if not active_players: return self.evaluate_state(game)
        player_moves_options = [game.get_valid_moves(p.id) for p in active_players]
        move_combinations = list(itertools.product(*player_moves_options))
        for combination in move_combinations:
            temp_game = game.clone()
            current_moves = {p.id: move for p, move in zip(active_players, combination)}
            temp_game.apply_moves(current_moves)
            value = max(value, self._min_value(temp_game, depth - 1, alpha, beta))
            if value >= beta: return value # Prune
            alpha = max(alpha, value)
        return value

class HybridAlphaBetaAgent(AlphaBetaAgent):
    def select_moves(self, game: KabaddiGame):
        if game.game_mode == 'simultaneous':
            return GreedyAgent(self.team).select_moves(game)
        else:
            return super().select_moves(game)

class MCTSNode:
    def __init__(self, game: KabaddiGame, parent=None, move=None):
        self.game = game
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.unexplored_moves = self._get_all_possible_moves()

    def _get_all_possible_moves(self):
        team_to_move = self.parent.game.state.current_player_team if self.parent else self.game.state.current_player_team
        active_players = [p for p in self.game.state.players.values() if p.team == team_to_move and not p.is_captured]
        if not active_players: return []
        player_moves_options = [self.game.get_valid_moves(p.id) for p in active_players]
        move_combinations = list(itertools.product(*player_moves_options))
        return [{p.id: move for p, move in zip(active_players, combo)} for combo in move_combinations]

    def select_child(self, exploration_constant=1.41):
        best_score = -1
        best_child = None
        for child in self.children:
            if child.visits == 0: return child
            exploit = child.wins / child.visits
            explore = exploration_constant * math.sqrt(math.log(self.visits) / child.visits)
            score = exploit + explore
            if score > best_score:
                best_score = score
                best_child = child
        return best_child

    def expand(self):
        if not self.unexplored_moves: return None
        move = self.unexplored_moves.pop()
        new_game = self.game.clone()
        new_game.apply_moves(move)
        if new_game.game_mode == 'turn_by_turn':
            new_game.state.current_player_team = 'B' if self.game.state.current_player_team == 'A' else 'A'
        child_node = MCTSNode(new_game, parent=self, move=move)
        self.children.append(child_node)
        return child_node

    def simulate(self):
        temp_game = self.game.clone()
        sim_agent_A = RandomAgent('A')
        sim_agent_B = RandomAgent('B')
        while temp_game.check_terminal_state() is None:
            if temp_game.game_mode == 'turn_by_turn':
                current_agent = sim_agent_A if temp_game.state.current_player_team == 'A' else sim_agent_B
                moves = current_agent.select_moves(temp_game)
                if not moves: break
                temp_game.apply_moves(moves)
                temp_game.state.current_player_team = 'B' if temp_game.state.current_player_team == 'A' else 'A'
            else:
                moves_A = sim_agent_A.select_moves(temp_game)
                moves_B = sim_agent_B.select_moves(temp_game)
                if not moves_A and not moves_B: break
                all_moves = {**moves_A, **moves_B}
                temp_game.apply_moves(all_moves)
        return temp_game.check_terminal_state()

    def backpropagate(self, result):
        node = self
        while node is not None:
            node.visits += 1
            team_that_made_move = node.parent.game.state.current_player_team if node.parent else self.game.state.current_player_team
            if team_that_made_move == result:
                node.wins += 1
            node = node.parent

class MCTSAgent(Agent):
    def __init__(self, team, time_limit=1.0):
        super().__init__(team)
        self.time_limit = time_limit

    def select_moves(self, game: KabaddiGame):
        root = MCTSNode(game)
        root.game.state.current_player_team = self.team
        start_time = time.time()
        while time.time() - start_time < self.time_limit:
            node = root
            while not node.unexplored_moves and node.children:
                node = node.select_child()
            if node.unexplored_moves:
                node = node.expand()
            if node:
                winner = node.simulate()
                if winner:
                    node.backpropagate(winner)
        if not root.children: return RandomAgent(self.team).select_moves(game)
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move


