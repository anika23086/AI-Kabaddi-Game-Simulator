import pandas as pd
from tqdm import tqdm
from game_environment import KabaddiGame
from agents import RandomAgent, GreedyAgent, AlphaBetaAgent, HybridAlphaBetaAgent, MCTSAgent

def run_single_match(agent_A_class, agent_B_class, game_mode, turn_limit, agent_A_params={}, agent_B_params={}):
    agent_A = agent_A_class(team='A', **agent_A_params)
    agent_B = agent_B_class(team='B', **agent_B_params)
    game = KabaddiGame(game_mode=game_mode, turn_limit=turn_limit)
    winner = game.run_game_loop(agent_A, agent_B)
    return winner

def run_tournament(agent_configs, num_games, game_mode, turn_limit=100):
    print(f"\n--- Starting Tournament: {game_mode.upper()} Mode ---")
    
    agent_names = [config['name'] for config in agent_configs]
    results = pd.DataFrame(0, index=agent_names, columns=agent_names, dtype=int)
    draws = pd.DataFrame(0, index=agent_names, columns=agent_names, dtype=int)
    
    total_matchups = len(agent_configs) * (len(agent_configs) - 1)
    if total_matchups == 0:
        print("Not enough agents to run a tournament.")
        return

    with tqdm(total=total_matchups * num_games, desc=f"Overall Progress ({game_mode})") as pbar:
        for i, agent_A_config in enumerate(agent_configs):
            for j, agent_B_config in enumerate(agent_configs):
                if i == j: continue

                wins_A = 0
                draw_count = 0 
                for _ in range(num_games):
                    winner = run_single_match(
                        agent_A_config['class'], 
                        agent_B_config['class'], 
                        game_mode, 
                        turn_limit,
                        agent_A_config.get('params', {}),
                        agent_B_config.get('params', {})
                    )
                    if winner == 'A':
                        wins_A += 1
                    elif winner == 'draw':
                        draw_count += 1
                    pbar.update(1)

                results.loc[agent_A_config['name'], agent_B_config['name']] = wins_A
                draws.loc[agent_A_config['name'], agent_B_config['name']] = draw_count
                
    print(f"\n--- Tournament Results: {game_mode.upper()} Mode ({num_games} games per matchup) ---")
    print("\nWIN COUNT (Row player vs Column player):")
    print(results)
    
    total_wins = results.sum(axis=1)
    total_losses = results.sum(axis=0)
    total_draws = draws.sum(axis=1)
    total_games_played = total_wins + total_losses + total_draws
    
    win_percentage = (total_wins / total_games_played.replace(0, 1)) * 100
    
    summary = pd.DataFrame({
        'Total Wins': total_wins,
        'Total Losses': total_losses,
        'Total Draws': total_draws,
        'Win %': win_percentage.round(1)
    })
    
    print("\nOVERALL SUMMARY:")
    print(summary.sort_values(by='Total Wins', ascending=False))
    print("-" * 50)

if __name__ == "__main__":
    GAMES_PER_MATCHUP = 20
    TURN_LIMIT = 100
    TIME_LIMIT = 0.5 
    
    turn_by_turn_agents = [
        {'name': 'Random', 'class': RandomAgent},
        {'name': 'Greedy', 'class': GreedyAgent},
        {'name': 'AlphaBeta (d=2)', 'class': AlphaBetaAgent, 'params': {'depth': 2}},
        {'name': 'MCTS (t=0.5s)', 'class': MCTSAgent, 'params': {'time_limit': TIME_LIMIT}} 
    ]
    run_tournament(turn_by_turn_agents, GAMES_PER_MATCHUP, 'turn_by_turn', TURN_LIMIT)

    simultaneous_agents = [
        {'name': 'Random', 'class': RandomAgent},
        {'name': 'Greedy', 'class': GreedyAgent},
        {'name': 'AlphaBeta (Naive)', 'class': AlphaBetaAgent, 'params': {'depth': 2}},
        {'name': 'AlphaBeta (Fallback)', 'class': HybridAlphaBetaAgent, 'params': {'depth': 2}},
        {'name': 'MCTS (t=0.5s)', 'class': MCTSAgent, 'params': {'time_limit': TIME_LIMIT}}
    ]
    run_tournament(simultaneous_agents, GAMES_PER_MATCHUP, 'simultaneous', TURN_LIMIT)

