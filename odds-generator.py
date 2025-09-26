# proto poker odds generator
# Created and run by chatGPT 5. Probably worth coding reviewing this and making changes

import random
import itertools
from collections import Counter
from typing import List, Tuple, Optional, Dict, Set, Union
from dataclasses import dataclass

# --------------------------
# Constants and Card class
# --------------------------
RANKS = list(range(2, 15))  # 2–14 (14 = Ace)
SUITS = ["♠", "♥", "♦", "♣"]
JOKER_RANK = "JOKER"
CARDS_PER_HAND = 8
CARDS_IN_EVALUATED_HAND = 5
JOKERS_PER_DECK = 2

@dataclass(frozen=True)
class Card:
    """Represents a playing card with rank and suit."""
    rank: Union[int, str]  # 2-14 for regular cards, "JOKER" for jokers
    suit: Optional[str]    # One of SUITS or None for jokers
    
    def __post_init__(self):
        if self.rank != JOKER_RANK and (not isinstance(self.rank, int) or self.rank not in RANKS):
            raise ValueError(f"Invalid rank: {self.rank}")
        if self.rank != JOKER_RANK and self.suit not in SUITS:
            raise ValueError(f"Invalid suit: {self.suit}")
        if self.rank == JOKER_RANK and self.suit is not None:
            raise ValueError("Jokers should not have a suit")
    
    def is_joker(self) -> bool:
        """Check if this card is a joker."""
        return self.rank == JOKER_RANK
    
    def __str__(self) -> str:
        if self.is_joker():
            return "🃏"
        return f"{self.rank}{self.suit}"
CARDS_PER_HAND = 8

def make_deck(num_players: int) -> List[Card]:
    """
    Create a deck with multiple standard decks plus jokers for multi-player games.
    Args:
        num_players: Number of players (determines how many deck copies to include)
    Returns:
        List of Card objects representing the complete deck
    Raises:
        ValueError: If num_players is not positive
    """
    if num_players <= 0:
        raise ValueError("Number of players must be positive")
        
    deck = []
    for _ in range(num_players):
        # Add standard deck
        for rank in RANKS:
            for suit in SUITS:
                deck.append(Card(rank, suit))
        # Add jokers
        for _ in range(JOKERS_PER_DECK):
            deck.append(Card(JOKER_RANK, None))
    return deck

# --------------------------
# Hand evaluation
# --------------------------
def is_rainbow_straight(hand: List[Card]) -> bool:
    """
    Check for rainbow straight: 4-card straight with all different suits plus a joker.
    Args:
        hand: List of 5 Card objects
    Returns:
        True if hand contains a rainbow straight, False otherwise
    """
    if len(hand) != CARDS_IN_EVALUATED_HAND:
        return False
        
    real_cards = [c for c in hand if not c.is_joker()]
    jokers = [c for c in hand if c.is_joker()]
    
    if len(real_cards) != 4 or len(jokers) != 1:
        return False
    
    # All suits must be different
    suits = [c.suit for c in real_cards]
    if len(set(suits)) != 4:
        return False
    
    # Check if ranks can form a straight with one joker filling a gap
    ranks = sorted([c.rank for c in real_cards])
    
    # Try each possible position for the joker
    for gap_pos in range(5):  # Joker can be at position 0,1,2,3,4
        test_ranks = ranks.copy()
        if gap_pos < 4:
            test_ranks.insert(gap_pos, 0)  # Placeholder for joker
        else:
            test_ranks.append(0)  # Joker at end
            
        # Check if we can assign joker value to make consecutive sequence
        for joker_val in range(2, 15):
            test_ranks[gap_pos] = joker_val
            test_ranks.sort()
            # Check if sorted ranks form a consecutive sequence
            if all(test_ranks[i+1] - test_ranks[i] == 1 for i in range(4)):
                # Ensure joker value doesn't duplicate existing ranks
                if joker_val not in ranks:
                    return True
                
    return False

def is_flush_five(hand: List[Card]) -> bool:
    """
    Check for flush five: All 5 cards identical in both rank and suit.
    Args:
        hand: List of 5 Card objects
    Returns:
        True if hand contains flush five, False otherwise
    """
    if len(hand) != CARDS_IN_EVALUATED_HAND:
        return False
        
    real_cards = [c for c in hand if not c.is_joker()]
    jokers = [c for c in hand if c.is_joker()]
    
    if not real_cards:
        return len(jokers) == 5  # All jokers case
    
    # Count identical rank-suit combinations
    card_counts = Counter(real_cards)
    if len(card_counts) > 1:
        return False  # Multiple different cards
    
    card, count = card_counts.most_common(1)[0]
    return count + len(jokers) >= 5

def is_five_of_a_kind(hand: List[Card]) -> bool:
    """
    Check for five of a kind: 5 cards with the same rank (any suits).
    Args:
        hand: List of 5 Card objects
    Returns:
        True if hand contains five of a kind, False otherwise
    """
    if len(hand) != CARDS_IN_EVALUATED_HAND:
        return False
        
    real_cards = [c for c in hand if not c.is_joker()]
    jokers = len([c for c in hand if c.is_joker()])
    
    if jokers >= 5:
        return True  # All jokers
    
    rank_counts = Counter([c.rank for c in real_cards])
    for rank, count in rank_counts.items():
        if count + jokers >= 5:
            return True
    return False

def is_flush_four(hand: List[Card]) -> bool:
    """
    Check for flush four: 4 cards identical in both rank and suit.
    Args:
        hand: List of 5 Card objects
    Returns:
        True if hand contains flush four, False otherwise
    """
    if len(hand) != CARDS_IN_EVALUATED_HAND:
        return False
        
    real_cards = [c for c in hand if not c.is_joker()]
    jokers = len([c for c in hand if c.is_joker()])
    
    card_counts = Counter(real_cards)
    for card, count in card_counts.items():
        if count + jokers >= 4:
            return True
    return False

def is_flush_house(hand: List[Card]) -> bool:
    """
    Check for flush house: Full house where all 5 cards are the same suit.
    A flush house requires:
    1. All 5 cards of the same suit
    2. 3 cards of one rank + 2 cards of another rank (full house pattern)
    Args:
        hand: List of 5 Card objects
    Returns:
        True if hand contains flush house, False otherwise
    """
    if len(hand) != CARDS_IN_EVALUATED_HAND:
        return False
        
    real_cards = [c for c in hand if not c.is_joker()]
    jokers = len([c for c in hand if c.is_joker()])
    
    if not real_cards:
        return jokers == 5  # All jokers case
    
    # Check if all real cards are same suit
    suits = [c.suit for c in real_cards]
    if len(set(suits)) > 1:
        return False  # Multiple suits
    
    # All cards must be same suit (real cards + jokers count as same suit)
    target_suit = suits[0] if suits else None
    if len(real_cards) + jokers != 5:
        return False
    
    # Check if we can form full house pattern (3+2) with available ranks
    ranks = [c.rank for c in real_cards]
    rank_counts = Counter(ranks)
    
    # Try to assign jokers to create 3+2 pattern
    return _can_form_full_house_pattern(rank_counts, jokers)

def _can_form_full_house_pattern(rank_counts: Dict[int, int], available_jokers: int) -> bool:
    """
    Helper function to check if jokers can be assigned to create full house pattern.
    Args:
        rank_counts: Counter of existing ranks
        available_jokers: Number of jokers available to assign
    Returns:
        True if a 3+2 full house pattern can be formed
    """
    ranks = list(rank_counts.keys())
    jokers_left = available_jokers
    
    # Case 1: No real cards - need to create 3+2 with all jokers
    if not ranks:
        return jokers_left == 5  # Can make 3+2 with 5 jokers
    
    # Case 2: One rank - try to make it the triple, create pair with jokers
    if len(ranks) == 1:
        rank = ranks[0]
        count = rank_counts[rank]
        # Make existing rank the triple
        if count + jokers_left >= 3:
            jokers_used_for_triple = max(0, 3 - count)
            jokers_remaining = jokers_left - jokers_used_for_triple
            return jokers_remaining >= 2  # Need 2 more for pair
        return False
    
    # Case 3: Two or more ranks - try different 3+2 combinations
    if len(ranks) >= 2:
        for triple_rank in ranks:
            for pair_rank in ranks:
                if triple_rank != pair_rank:
                    triple_count = rank_counts[triple_rank]
                    pair_count = rank_counts[pair_rank]
                    
                    jokers_for_triple = max(0, 3 - triple_count)
                    jokers_for_pair = max(0, 2 - pair_count)
                    
                    if jokers_for_triple + jokers_for_pair <= jokers_left:
                        return True
    
    # Case 4: Need to create new rank for pair/triple with jokers
    if len(ranks) == 1:
        return False  # Already handled above
    
    return False

def classify_illegal(hand: List[Card]) -> Optional[str]:
    """
    Classify a 5-card hand as one of the illegal hand types.
    
    Checks hands in order of rarity (most rare first):
    1. Flush Five - All 5 cards identical rank & suit
    2. Five of a Kind - 5 cards same rank, any suits  
    3. Flush House - Full house, all same suit
    4. Flush Four - 4 cards identical rank & suit
    5. Rainbow Straight - 4-card straight, all different suits + joker
    
    Args:
        hand: List of 5 Card objects
        
    Returns:
        String name of illegal hand type, or None if not illegal
    """
    if is_flush_five(hand):
        return "Flush Five"
    if is_five_of_a_kind(hand):
        return "Five of a Kind"  
    if is_flush_house(hand):
        return "Flush House"
    if is_flush_four(hand):
        return "Flush Four"
    if is_rainbow_straight(hand):
        return "Rainbow Straight"
    return None

# --------------------------
# Simulation helpers
# --------------------------
def best_illegal_from_hand(cards: List[Card]) -> Optional[str]:
    """
    Check all 5-card subsets of a hand for the best illegal classification.
    
    Args:
        cards: List of Card objects (typically 8 cards per hand)
        
    Returns:
        String name of best illegal hand found, or None if no illegal hands
    """
    if len(cards) < CARDS_IN_EVALUATED_HAND:
        return None
        
    # Check all possible 5-card combinations
    for combo in itertools.combinations(cards, CARDS_IN_EVALUATED_HAND):
        label = classify_illegal(list(combo))
        if label:
            return label  # Return first illegal hand found (they're checked by rarity)
    return None

def simulate_round(num_players: int = 4) -> List[Optional[str]]:
    """
    Simulate one round of poker with multiple players.
    
    Args:
        num_players: Number of players in the round
        
    Returns:
        List of illegal hand classifications (or None) for each player
        
    Raises:
        ValueError: If num_players is not positive or deck is too small
    """
    if num_players <= 0:
        raise ValueError("Number of players must be positive")
        
    deck = make_deck(num_players)
    
    if len(deck) < num_players * CARDS_PER_HAND:
        raise ValueError(f"Deck too small for {num_players} players")
        
    random.shuffle(deck)
    results = []
    
    for player in range(num_players):
        start_idx = player * CARDS_PER_HAND
        end_idx = start_idx + CARDS_PER_HAND
        player_hand = deck[start_idx:end_idx]
        result = best_illegal_from_hand(player_hand)
        results.append(result)
        
    return results

def run_simulation(trials: int = 10000, num_players: int = 4) -> Tuple[int, Counter, int]:
    """
    Run multiple rounds of poker simulation to calculate illegal hand probabilities.
    
    Args:
        trials: Number of simulation rounds to run
        num_players: Number of players per round
        
    Returns:
        Tuple of (rounds_with_illegal_hands, illegal_hand_counts, total_trials)
        
    Raises:
        ValueError: If trials or num_players are not positive
    """
    if trials <= 0:
        raise ValueError("Number of trials must be positive")
    if num_players <= 0:
        raise ValueError("Number of players must be positive")
        
    illegal_hand_counts = Counter()
    rounds_with_illegal = 0
    
    for _ in range(trials):
        round_results = simulate_round(num_players)
        illegal_results = [result for result in round_results if result is not None]
        
        if illegal_results:
            rounds_with_illegal += 1
            illegal_hand_counts.update(illegal_results)
            
    return rounds_with_illegal, illegal_hand_counts, trials

# --------------------------
# Example run
# --------------------------
if __name__ == "__main__":
    for n in range(2, 6):
        rounds_with_illegal, counts, trials = run_simulation(2000, num_players=n)
        print(f"\nPlayers: {n}")
        print(f"Rounds with ≥1 illegal: {rounds_with_illegal}/{trials} "
              f"({rounds_with_illegal/trials:.4%})")
        total_hands = trials * n
        for k, v in counts.items():
            print(f"{k}: {v} hands ({v/total_hands:.4%} per hand)")
