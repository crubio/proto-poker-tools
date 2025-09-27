# Poker Simulator Development Roadmap

## Project Overview
A comprehensive poker simulator featuring traditional poker hands with joker support, exotic "illegal" hands, mod cards, character classes, and tournament systems.

## Current Status ✅

### Core Systems Implemented
- **Card System**: Standard 52-card deck + 2 jokers
- **Custom Decks**: 7 specialty decks (Madness, DarkSoul, SeeingRed, etc.)
- **Hand Evaluation**: Standard poker hands with joker support
- **Character Classes**: 9 unique classes with special abilities
- **Mod Cards**: 3 types with various effects
- **Tournament System**: Multi-round tournaments with statistics
- **Visualization**: Interactive dashboards with Plotly

### Configuration Constants
```python
MIN_REAL_CARDS = 1      # Minimum real cards per player
MAX_REAL_CARDS = 8      # Maximum real cards per player  
TOTAL_HAND_SIZE = 8     # Total cards in each player's hand
MAX_DISPLAY_CARDS = 6   # Cards shown in UI display
```

## Phase 1: Extended Game Rules 🎮

### 1.1 Enhanced Round Structure
- **Starting Hand**: Players begin each round with 1 guaranteed mod card + 7 dealt cards
- **End Phase Evaluation**: Knight (showdown) and Queen (payout) mod cards trigger and burn
- **Mod Economy**: Winner draws 2 mod cards, non-folded players draw 1
- **Deck Cycling**: Shuffle mods back into deck (4 random mods per 4 players)

### 1.2 Strategic Implications
- **Opening Strategy**: Tactical use of guaranteed starting mod card
- **Timing Decisions**: When to play Knight/Queen mods vs saving them
- **Risk/Reward**: Folding prevents mod draw, encouraging participation
- **Market Dynamics**: Constant mod circulation prevents scarcity

### 1.3 Implementation Requirements
- Fold mechanic tracking system
- Knight/Queen mod evaluation and burn system
- End-of-round mod redistribution logic
- Enhanced deck shuffling with returned mod cards

---

## Phase 2: Betting & Folding System 🎯

### Overview
Implement character-driven betting and folding mechanics that integrate with the existing mod card economy and tournament structure.

### 2.1 Betting System Design

#### Character Betting Profiles
Each character class will have distinct betting behaviors:

- **🃏 Jester**: Wildcard strategy (fold_threshold: 15%, aggression: 80%, bluff_rate: 40%)
- **⚔️ Knight**: Conservative strategy (fold_threshold: 60%, aggression: 30%, bluff_rate: 10%) 
- **🛡️ Warrior**: Aggressive strategy (fold_threshold: 30%, aggression: 70%, bluff_rate: 25%)
- **🥷 Rogue**: Balanced strategy (fold_threshold: 40%, aggression: 50%, bluff_rate: 30%)

#### Decision Algorithm Factors
```python
def make_betting_decision(player, hand_strength, chips_remaining, pot_size, to_call, num_mod_cards):
    # Considers:
    # - Hand strength (0.0-1.0 poker hand quality)
    # - Character betting profile 
    # - Chip situation (stack-to-pot ratio)
    # - Mod card utility (more mods = more likely to stay)
    # - Tournament position
```

#### Betting Actions
- **Fold**: Exit round, lose current bet
- **Check**: No additional bet (when possible)
- **Call**: Match current bet
- **Bet**: Initiate betting 
- **Raise**: Increase current bet
- **All-In**: Bet all remaining chips

### 2.2 Folding Mechanics

#### Anti-Fold Incentives
The game design encourages staying in rounds:
- **Participation Bonus**: +1 mod card for staying in round
- **Showdown Experience**: +2 mods if you make it to showdown (winner gets 4 total)
- **Utility Preservation**: Mod cards can still activate even with weak poker hands

#### Folding Penalties
- **Mod Draw Loss**: Folded players don't draw mods at round end
- **Ability Cooldown**: Character abilities have 1-round cooldown after fold
- **No Chip Penalty**: Direct chip loss only from forfeited bets

#### Strategic Considerations
- Folding rare due to mod card economy incentives
- Only beneficial when avoiding large chip losses
- Character-specific fold thresholds based on chip conservation values

### 2.3 Implementation Architecture

#### Enhanced PlayerCharacterCard
```python
class PlayerCharacterCard(BaseModel):
    # ...existing fields...
    current_chips: int = DEFAULT_STARTING_CHIPS
    betting_strategy: Optional[BettingStrategy] = None
    ability_on_cooldown: bool = False
```

#### Betting Strategy Enum
```python
class BettingStrategy(str, enum.Enum):
    Conservative = "Conservative"    # Fold/check frequently, small bets
    Balanced = "Balanced"           # Standard poker strategy
    Aggressive = "Aggressive"       # Large bets, rare folds  
    Wildcard = "Wildcard"          # Unpredictable, high variance
```

### 2.4 Integration Points

#### Tournament Flow Updates
1. **Betting Rounds**: Add betting phases between card dealing and hand evaluation
2. **Chip Tracking**: Monitor chip counts throughout tournament
3. **Fold Tracking**: Record which players folded for mod distribution
4. **Pot Management**: Calculate pot sizes and payouts

#### Character Ability Integration
- **Jester**: Values mod cards extremely highly in betting decisions
- **Knight**: Highly chip-conscious, factors stack size heavily
- **Warrior**: Pushes advantages aggressively, no fold cooldown penalty
- **Rogue**: Uses information and timing strategically

### 2.5 Success Metrics
- **Participation Rate**: 80%+ players staying in rounds (validates anti-fold design)
- **Character Differentiation**: Measurable differences in betting patterns by class
- **Strategic Depth**: Multiple viable approaches (chip conservation vs mod accumulation)
- **Tournament Balance**: No single strategy dominates across all scenarios

---

## Phase 3: Advanced Features 🚀

### 3.1 Exotic Hand Types
Implement "illegal" poker hands:
- **Flush Five**: Five cards of same suit + same rank
- **Five of a Kind**: Five identical cards (with jokers)
- **Rainbow Straight**: Straight with all different suits
- **Sandwich Hand**: Pairs on outside, different ranks in middle
- **Flush House**: Full house where all cards same suit

### 3.2 Advanced Mod Cards
- **Global Effects**: Cards that affect entire table
- **Conditional Triggers**: Mods that activate based on game state
- **Chain Effects**: Mods that trigger other mods
- **Persistent Effects**: Mods that last multiple rounds

### 3.3 Tournament Formats
- **Single Elimination**: Winner-take-all brackets
- **Swiss System**: All players play same number of rounds
- **League Play**: Season-long competition with standings
- **Team Tournaments**: Character class synergies

---

## Phase 4: Polish & Deployment 🎨

### 4.1 User Interface
- **Web Interface**: Browser-based game client
- **Real-time Updates**: Live tournament tracking
- **Player Profiles**: Statistics and achievement tracking
- **Mobile Support**: Responsive design for tablets/phones

### 4.2 AI & Balance
- **Machine Learning**: Train AI players on tournament data
- **Balance Testing**: Automated tournament simulations
- **Meta Analysis**: Track strategy evolution over time
- **Dynamic Balancing**: Adjust card effects based on win rates

### 4.3 Multiplayer Support
- **Network Play**: Real-time multiplayer tournaments
- **Spectator Mode**: Watch tournaments in progress
- **Replay System**: Review past games and hands
- **Leaderboards**: Global and local rankings

---

## Technical Architecture

### Current Stack
- **Language**: Python 3.x
- **Data Models**: Pydantic for type safety
- **Visualization**: Plotly for interactive charts
- **Development**: Jupyter Notebook for prototyping

### Future Stack Considerations
- **Backend**: FastAPI or Flask for web services
- **Database**: PostgreSQL for tournament/player data
- **Frontend**: React or Vue.js for user interface
- **Deployment**: Docker containers on cloud platform

---

## Success Criteria

### Phase 1 Goals
- [ ] Extended round rules fully implemented
- [ ] Mod economy working as designed
- [ ] All character classes balanced and viable

### Phase 2 Goals  
- [ ] Betting system creates meaningful strategic decisions
- [ ] 80%+ participation rate maintained
- [ ] Character betting profiles clearly differentiated
- [ ] Tournament balance across multiple strategies

### Long-term Vision
Create the most strategically rich and engaging poker variant ever designed, combining traditional poker skill with unique utility mechanics and character-driven gameplay.