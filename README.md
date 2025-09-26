# Proto Poker Tools

A poker simulation adding extra layers of play for a more chaotic session. Includes illegal & exotic hand scoring, modifier cards, character classes & abilities, etc. Aims to be more rogue-like than poker.

## 🎮 Features

- **Traditional Poker + Jokers**: Classic poker hands with wild card support
- **Exotic "Illegal" Hands**: Unique hands like Rainbow Straight, Flush Five, and Sandwich Hand
- **Mod Card System**: Special cards that modify gameplay (Extra Draw, Sneaky Swap, Royal Dividend)
- **Character Classes**: Players with unique abilities (Rogue, Warrior, Jester, etc.)
- **Multi-Round Tournaments**: Points and chips system for competitive play
- **Full Type Safety**: Comprehensive Pydantic models with runtime validation

## 📁 Project Structure

```
proto-poker-tools/
├── README.md                           # This file
├── odds-generator.py                   # Poker odds calculation utilities
├── round-simulator.py                  # Main poker simulation engine
└── poker-sim.ipynb                     # Clean version for JupyterLab
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ 
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/crubio/proto-poker-tools.git
cd proto-poker-tools
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install pydantic jupyterlab ipywidgets plotly pandas
```

### Running the Simulation

#### Option 1: Jupyter Notebook (Recommended)
```bash
jupyter lab
# Open poker-sim-clean.ipynb and run the cells
```

#### Option 2: Python Script
```bash
python round-simulator.py
```

## 🎯 What Makes This Special

### Exotic Hand Types
Beyond traditional poker, the system includes creative hands:
- **Flush Five**: All 5 cards identical rank AND suit
- **Rainbow Straight**: Straight with all four suits represented  
- **Flush House**: Full house where all cards are same suit
- **Sandwich Hand**: Three-of-a-kind + cards completing a straight

### Dynamic Gameplay
- **Mod Cards**: Special effects that activate during gameplay
- **Character Abilities**: Each player class has unique powers
- **Emergent Strategy**: Simple rules create complex interactions

### Technical Excellence
- **Type Safety**: Full Pydantic validation and type hints
- **Extensible Design**: Easy to add new cards, abilities, and hands
- **Interactive Analysis**: Jupyter notebooks for exploration

## 🃏 Game Flow

1. **Deal Phase**: Players receive mix of real cards + mod cards
2. **Mod Effects**: Special cards activate (Extra Draw, Card Swap, etc.)
3. **Character Abilities**: Class powers trigger (Rogue steals, Warrior reveals)
4. **Hand Evaluation**: Best 5-card combination from available cards
5. **Scoring**: Winner gets points and bonus effects

## 📊 Character Classes (more to come)

Rogues, Wizards, Warriors and more. All will have a special ability to play during their turn to flip the tables.

## 🔧 Technical Details

### Core Technologies
- **Python 3.8+**: Main language
- **Pydantic**: Data validation and type safety
- **Jupyter**: Interactive development and analysis
- **Plotly**: Interactive visualizations

### Architecture
- **Enum-based Design**: Type-safe game entities
- **Functional Approach**: Pure functions for game logic  
- **Modular Structure**: Easy to extend and modify

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎲 Example Output

```
STARTING ROUND SIMULATION
======================================

PHASE 1: DEALING HANDS
------------------------------
Scruffy McMuffins (Rogue):
  Real cards: AS, KH, QD, JC, 10S...
  Mod cards: ['Extra Draw']

PHASE 2: APPLYING MOD EFFECTS  
------------------------------
  -> Scruffy McMuffins draws 9H (Extra Draw)

PHASE 3: CHARACTER ABILITIES
------------------------------
  -> Scruffy McMuffins (Rogue) steals 8D from Sir Whiskers

PHASE 4: HAND EVALUATION
------------------------------
  Scruffy McMuffins: Royal Flush
  Patches: Two Pair
  Sir Whiskers: High Card

WINNER: Scruffy McMuffins with Royal Flush!
```