import random
import copy

class Player:
    def __init__(self, player_id, team, start_pos):
        self.id = player_id
        self.team = team
        self.pos = start_pos
        self.has_gold = False
        self.is_captured = False

    def __repr__(self):
        return f"Player({self.id}, Team: {self.team}, Pos: {self.pos}, Gold: {self.has_gold}, Captured: {self.is_captured})"

class GameState:
    def __init__(self, grid_size=(10, 10)):
        self.grid_size = grid_size
        self.half_way_x = grid_size[0] // 2
        
        self.players = {
            'A1': Player('A1', 'A', (1, 2)),
            'A2': Player('A2', 'A', (1, 7)),
            'B1': Player('B1', 'B', (grid_size[0] - 2, 2)),
            'B2': Player('B2', 'B', (grid_size[0] - 2, 7)),
        }
        self.gold_pos = {
            'A': (0, 5),
            'B': (grid_size[0] - 1, 5)
        }
        self.turn = 0
        self.current_player_team = 'A' 

    def is_in_enemy_territory(self, player):
        if player.team == 'A':
            return player.pos[0] >= self.half_way_x
        else:
            return player.pos[0] < self.half_way_x

    def is_in_home_territory(self, player):
        return not self.is_in_enemy_territory(player)

class KabaddiGame:
    def __init__(self, game_mode='turn_by_turn', turn_limit=100):
        self.state = GameState()
        self.game_mode = game_mode
        self.turn_limit = turn_limit

    def clone(self):
        return copy.deepcopy(self)

    def get_valid_moves(self, player_id):
        player = self.state.players.get(player_id)
        if not player or player.is_captured:
            return []

        x, y = player.pos
        potential_moves = [
            (x, y),      # Stay
            (x + 1, y),  # Down
            (x - 1, y),  # Up
            (x, y + 1),  # Right
            (x, y - 1),  # Left
        ]

        valid_moves = []
        for move_x, move_y in potential_moves:
            if 0 <= move_x < self.state.grid_size[0] and 0 <= move_y < self.state.grid_size[1]:
                valid_moves.append((move_x, move_y))
        
        return valid_moves

    def apply_moves(self, moves):
        for player_id, new_pos in moves.items():
            if player_id in self.state.players and not self.state.players[player_id].is_captured:
                self.state.players[player_id].pos = new_pos

        for player in self.state.players.values():
            if player.is_captured or player.has_gold:
                continue
            
            opponent_team = 'B' if player.team == 'A' else 'A'
            opponent_gold_pos = self.state.gold_pos.get(opponent_team)
            
            if opponent_gold_pos and player.pos == opponent_gold_pos:
                player.has_gold = True
                self.state.gold_pos[opponent_team] = None

        player_positions = {}
        for p_id, p in self.state.players.items():
            if not p.is_captured:
                if p.pos not in player_positions:
                    player_positions[p.pos] = []
                player_positions[p.pos].append(p)
        
        for pos, players_on_square in player_positions.items():
            if len(players_on_square) > 1:
                teams_on_square = {p.team for p in players_on_square}
                if len(teams_on_square) > 1:
                    for p in players_on_square:
                        if self.state.is_in_enemy_territory(p):
                            p.is_captured = True
        
        self.state.turn += 1

    def check_terminal_state(self):
        for player in self.state.players.values():
            if player.has_gold and self.state.is_in_home_territory(player):
                return player.team

        active_players_A = [p for p in self.state.players.values() if p.team == 'A' and not p.is_captured]
        active_players_B = [p for p in self.state.players.values() if p.team == 'B' and not p.is_captured]

        if not active_players_A:
            return 'B'
        if not active_players_B:
            return 'A'

        if self.state.turn >= self.turn_limit:
            return 'draw'

        return None

    def run_game_loop(self, agent_A, agent_B):
        winner = None
        while winner is None:
            if self.game_mode == 'turn_by_turn':
                current_agent = agent_A if self.state.current_player_team == 'A' else agent_B
                moves = current_agent.select_moves(self)
                if not moves: 
                    break
                self.apply_moves(moves)
                self.state.current_player_team = 'B' if self.state.current_player_team == 'A' else 'A'
            else: 
                moves_A = agent_A.select_moves(self)
                moves_B = agent_B.select_moves(self)
                if not moves_A and not moves_B:
                    break
                all_moves = {**moves_A, **moves_B}
                self.apply_moves(all_moves)
            
            winner = self.check_terminal_state()
        
        return winner if winner else 'draw'

