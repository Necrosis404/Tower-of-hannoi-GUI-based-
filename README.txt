# AUTHOR-- SAIKAT SAHA 22053184 CSE-16
### NUMBER OF TEAM MEMBERS:- 1

# Tower of Hanoi AI Solver

A Python application that demonstrates traditional search algorithms (BFS, DFS, and Bidirectional Search) for solving the Tower of Hanoi puzzle.

## Features

- Interactive Tower of Hanoi game with customizable number of disks
- Three hand-coded search algorithms:
  - Breadth-First Search (BFS)
  - Depth-First Search (DFS)
  - Bidirectional Search
- GUI interface with visualization of the puzzle state
- Ability to randomize the initial state
- Start, pause, and resume search capabilities
- Gif animations

## Project Structure

- `main.py` - Entry point for the application
- `hanoi_game.py` - Tower of Hanoi game logic
- `hanoi_search.py` - Implementation of search algorithms
- `hanoi_gui.py` - GUI implementation using Tkinter
- `requirements.txt` - List of dependencies

## Prerequisites
- Python 3.7 or higher
- PIL (Pillow) for image processing


## Usage
pip install -r requirements.txt

Run the application:
python main.py


### Controls

- Number of Disks: Select the number of disks (2-7)
- Algorithm: Choose between BFS, DFS, and Bidirectional Search
- Randomize: Create a random initial state
- Start Search: Begin the selected search algorithm
- Pause/Resume: Temporarily halt or continue the search
- Reset: Reset the game to the initial state
- Create GIF: Generate an animation of the solution

## How It Works

1. The Tower of Hanoi puzzle is represented as a state-space search problem
2. Each state is a configuration of disks on the three towers
3. Transitions between states are valid moves of disks
4. The goal state has all disks on the rightmost tower
5. Search algorithms explore the state space to find a path from the initial state to the goal state
6. The solution is a sequence of moves that transforms the initial state to the goal state

## Example Generated GIF

The application creates GIF animations showing the step-by-step solution:
- Each frame represents a state
- Frames are played in sequence to visualize the solution
- The GIF is saved with a timestamp in the filename