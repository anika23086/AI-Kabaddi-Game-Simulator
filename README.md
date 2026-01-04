# AI-Kabaddi-Game-Simulator
This project is a Python-based simulation environment for a 2v2 variant of Kabaddi. It features a modular architecture designed to benchmark different Artificial Intelligence strategies, ranging from simple heuristics to complex tree searches, across different execution models.

## The Game: Kabaddi Variant
The game is played on a grid divided into two halves.
- Teams: Two teams (A and B), each with 2 players.
- Objective: Steal the opponent's gold treasure and return it to home territory.
- Rules:
    - Players move one grid space per turn (Up, Down, Left, Right, or Stay).
    - Players can be captured and removed if an opponent moves onto their square while they are in enemy territory.
    - Supports two modes: Turn-by-Turn (sequential) and Simultaneous (parallel).

## AI Agents Implemented
**1. Random Agent:** 
  - Serves as the performance baseline.
  - Selects moves uniformly at random from all valid options.
    
**2. Greedy Agent (Heuristic-based)**
  - Uses a weighted evaluation function to score the board state one move ahead.
  - Weights priorities: Survival (-1000) > Objective (+500) > Proximity to Gold/Home.
    
**3. Alpha-Beta Pruning Agent**
  - Explores the game tree to a fixed depth (default d=2).
  - Hybrid Logic: In Turn-by-Turn mode, it uses deep-search minimax to anticipate optimal opponent counters. In Simultaneous mode, it utilizes a "graceful degradation" strategy,     falling back to Greedy logic to maintain robustness in unpredictable environments.
    
**4. Monte Carlo Tree Search (MCTS)**
  - A probabilistic search algorithm that utilizes random rollouts (simulations).
  - Optimization: Implemented a time-bounded search (0.5s per move) rather than a fixed iteration count, allowing for deeper exploration on capable hardware.

## Experimental Results
A round-robin tournament was conducted with 20 games per matchup.

### Turn-by-Turn Mode:
In deterministic environments, deep-planning agents dominated the field.
| Agent              | Total Wins | Win %  |
|--------------------|-----------:|-------:|
| Alpha-Beta (d=2)   | 24         | 100%   |
| Greedy             | 19         | 96.4%  |
| MCTS (t = 0.5s)    | 6          | 13.0%  |
| Random             | 0          | 0.0%   |

### Simultaneous Mode
This mode tests the resilience of agents under uncertainty. The Hybrid Alpha-Beta successfully adapted to match the Greedy baseline, avoiding the failures typically associated with pure prediction models in parallel execution.
| Agent                 | Total Wins | Win %  |
|-----------------------|-----------:|-------:|
| Greedy                | 19         | 100%   |
| Alpha-Beta (Hybrid)   | 19         | 100%   |
| Random                | 0          | 0.0%   |

## Analysis and Findings
The project demonstrates that Alpha-Beta Pruning is the optimal choice for sequential, deterministic games. However, its reliance on perfect prediction makes it brittle in simultaneous environments. By engineering a Hybrid Adaptive Model, we achieved a performance recovery from 0% to 100% win rate in simultaneous play, proving that adaptability is as crucial as depth in AI design.
