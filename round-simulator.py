from pydantic import BaseModel
from typing import List, Optional
import random
from itertools import combinations

# -----------------------------
# Types
# -----------------------------
class ModCard(BaseModel):
    name: str
    description: str
    effect: str
    type: str
    flavorType: str
    rarity: str
    burnOnUse: Optional[bool] = False

class PlayerCharacterCard(BaseModel):
    name: str
    char_class: str
    deck_modifier: Optional[str]
    ability: str
    starting_chips: int = 100
    description: Optional[str] = None

# -----------------------------
# Helper: evaluate illegal/exotic hands
# -----------------------------
def card_rank(card: str) -> int:
    if card == "JOKER":
        return 0  # Special value for jokers
    rank = card[:-1]
    if rank in ["J","Q","K","A"]:
        return {"J":11,"Q":12,"K":13,"A":14}[rank]
    return int(rank)

def evaluate_standard_poker(hand: List[str]) -> str:
    """Evaluate standard poker hands with joker support."""
    jokers = [card for card in hand if card == "JOKER"]
    real_cards = [card for card in hand if card != "JOKER"]
    num_jokers = len(jokers)
    
    if num_jokers == 0:
        # No jokers - use original logic
        suits = [card[-1] for card in hand]
        ranks = [card_rank(card) for card in hand]
        rank_counts = {}
        for r in ranks:
            rank_counts[r] = rank_counts.get(r, 0) + 1
        
        sorted_ranks = sorted(ranks)
        is_flush = len(set(suits)) == 1
        is_straight = all(sorted_ranks[i+1] - sorted_ranks[i] == 1 for i in range(4))
    else:
        # With jokers - evaluate best possible hand
        suits = [card[-1] for card in real_cards]
        ranks = [card_rank(card) for card in real_cards]
        rank_counts = {}
        for r in ranks:
            rank_counts[r] = rank_counts.get(r, 0) + 1
        
        # Check different ways to use jokers
        return _evaluate_standard_poker_with_jokers(ranks, suits, num_jokers)
    
    # Check for straight flush
    if is_straight and is_flush:
        if sorted_ranks == [10, 11, 12, 13, 14]:  # Royal flush
            return "Royal Flush"
        return "Straight Flush"
    
    # Check for four of a kind
    if 4 in rank_counts.values():
        return "Four of a Kind"
    
    # Check for full house
    if sorted(rank_counts.values()) == [2, 3]:
        return "Full House"
    
    # Check for flush
    if is_flush:
        return "Flush"
    
    # Check for straight
    if is_straight:
        return "Straight"
    
    # Check for three of a kind
    if 3 in rank_counts.values():
        return "Three of a Kind"
    
    # Check for pairs
    pair_count = sum(1 for count in rank_counts.values() if count == 2)
    if pair_count == 2:
        return "Two Pair"
    elif pair_count == 1:
        return "One Pair"
    
    return "High Card"

def _evaluate_standard_poker_with_jokers(ranks: List[int], suits: List[str], num_jokers: int) -> str:
    """Helper function to evaluate standard poker hands with jokers."""
    rank_counts = {}
    for r in ranks:
        rank_counts[r] = rank_counts.get(r, 0) + 1
    
    # Try to make the best possible hand with jokers
    # Priority order: Royal Flush -> Straight Flush -> Four of a Kind -> Full House -> etc.
    
    # Check for possible straight flush / royal flush
    if len(set(suits)) <= 1:  # All real cards same suit
        sorted_ranks = sorted(ranks)
        # Try to complete straights with jokers
        for start_rank in range(2, 11):  # Different starting points for straights
            straight_ranks = list(range(start_rank, start_rank + 5))
            if all(r <= 14 for r in straight_ranks):  # Valid ranks
                matched = sum(1 for r in straight_ranks if r in ranks)
                if matched + num_jokers >= 5:
                    if straight_ranks == [10, 11, 12, 13, 14]:
                        return "Royal Flush"
                    return "Straight Flush"
    
    # Check for Four of a Kind
    for rank in set(ranks):
        if rank_counts[rank] + num_jokers >= 4:
            return "Four of a Kind"
    
    # Check for Full House (3+2)
    if _can_make_full_house_with_jokers(rank_counts, num_jokers):
        return "Full House"
    
    # Check for Flush
    if len(set(suits)) <= 1 and len(ranks) + num_jokers >= 5:
        return "Flush"
    
    # Check for Straight
    if _can_make_straight_with_jokers(ranks, num_jokers):
        return "Straight"
    
    # Check for Three of a Kind
    for rank in set(ranks):
        if rank_counts[rank] + num_jokers >= 3:
            return "Three of a Kind"
    
    # Check for Two Pair
    pairs = 0
    jokers_used = 0
    for rank, count in rank_counts.items():
        if count == 2:
            pairs += 1
        elif count == 1 and jokers_used < num_jokers:
            pairs += 1
            jokers_used += 1
    
    if pairs >= 2:
        return "Two Pair"
    
    # Check for One Pair
    for rank in set(ranks):
        if rank_counts[rank] + num_jokers >= 2:
            return "One Pair"
    
    return "High Card"

def _can_make_full_house_with_jokers(rank_counts: dict, num_jokers: int) -> bool:
    """Check if we can make a full house (3+2) with available jokers."""
    ranks = list(rank_counts.keys())
    
    # Try different combinations for 3+2
    for triple_rank in ranks:
        for pair_rank in ranks:
            if triple_rank != pair_rank:
                triple_need = max(0, 3 - rank_counts[triple_rank])
                pair_need = max(0, 2 - rank_counts[pair_rank])
                if triple_need + pair_need <= num_jokers:
                    return True
    
    # Try using jokers to create a new rank for pair
    if len(ranks) >= 1:
        for triple_rank in ranks:
            triple_need = max(0, 3 - rank_counts[triple_rank])
            if triple_need + 2 <= num_jokers:  # +2 for new pair
                return True
    
    return False

def _can_make_straight_with_jokers(ranks: List[int], num_jokers: int) -> bool:
    """Check if we can make a straight with available jokers."""
    if len(ranks) + num_jokers < 5:
        return False
    
    sorted_ranks = sorted(set(ranks))
    
    # Try different starting points for 5-card straights
    for start_rank in range(2, 11):  # A-2-3-4-5 through 10-J-Q-K-A
        straight_ranks = list(range(start_rank, start_rank + 5))
        matched = sum(1 for r in straight_ranks if r in ranks)
        if matched + num_jokers >= 5:
            return True
    
    return False

def evaluate_illegal_exotic(hand: List[str]) -> str:
    suits = [card[-1] if card != "JOKER" else None for card in hand]
    ranks = [card_rank(card) for card in hand]
    
    # Separate jokers from real cards
    jokers = [card for card in hand if card == "JOKER"]
    real_cards = [card for card in hand if card != "JOKER"]
    real_ranks = [card_rank(card) for card in real_cards]
    real_suits = [card[-1] for card in real_cards]
    
    rank_counts = {r:real_ranks.count(r) for r in set(real_ranks)}
    
    # Rainbow Straight: Straight where all four suits are represented
    if len(jokers) <= 1:  # Can work with 0 or 1 joker
        if len(jokers) == 0:
            # No jokers - check if it's a 5-card straight with all 4 suits represented
            if (len(set(real_suits)) == 4 and len(real_ranks) == 5):
                sorted_ranks = sorted(real_ranks)
                if all(sorted_ranks[i+1] - sorted_ranks[i] == 1 for i in range(4)):
                    return "Rainbow Straight"
        else:
            # One joker - check if real cards can form straight with all 4 suits
            if len(set(real_suits)) == 4 and len(real_cards) == 4:
                for joker_rank in range(2, 15):
                    test_sequence = sorted(real_ranks + [joker_rank])
                    if all(test_sequence[i+1] - test_sequence[i] == 1 for i in range(4)):
                        return "Rainbow Straight"
    
    # Check for exotic hands with joker support
    num_jokers = len(jokers)
    
    # Flush Five: All 5 cards identical rank & suit
    if num_jokers > 0:
        # Check if we can make flush five with jokers
        for card in set(real_cards):
            if real_cards.count(card) + num_jokers >= 5:
                return "Flush Five"
    else:
        # No jokers - check for natural flush five
        if len(set(real_suits)) == 1 and len(set(real_ranks)) == 1:
            return "Flush Five"
    
    # Five of a Kind: 5 cards same rank (any suits)
    if num_jokers > 0:
        for rank in set(real_ranks):
            if real_ranks.count(rank) + num_jokers >= 5:
                return "Five of a Kind"
    else:
        if 5 in rank_counts.values():
            return "Five of a Kind"
    
    # Flush House: Full house all same suit
    if _check_flush_house_with_jokers(real_cards, real_ranks, real_suits, num_jokers):
        return "Flush House"
    
    # Flush Four: 4 cards identical rank & suit
    if num_jokers > 0:
        for card in set(real_cards):
            if real_cards.count(card) + num_jokers >= 4:
                return "Flush Four"
    else:
        if len(set(real_suits)) == 1 and 4 in rank_counts.values():
            return "Flush Four"
    
    # Skipping Straight: Every other rank (2-4-6-8-10 or 3-5-7-9-J)
    if _check_skipping_straight_with_jokers(real_ranks, num_jokers):
        return "Skipping Straight"
    
    # Even Straight: Only even ranks (2-4-6-8-10)
    if _check_even_straight_with_jokers(real_ranks, num_jokers):
        return "Even Straight"
    
    # Odd Straight: Only odd ranks (3-5-7-9-J)  
    if _check_odd_straight_with_jokers(real_ranks, num_jokers):
        return "Odd Straight"
    
    # Sandwich Hand: Three-of-a-kind + two outer cards completing straight
    if _check_sandwich_hand_with_jokers(real_ranks, num_jokers):
        return "Sandwich Hand"
    
    return "High Card"

def _check_flush_house_with_jokers(real_cards: List[str], real_ranks: List[int], real_suits: List[str], num_jokers: int) -> bool:
    """Check for flush house: full house where all cards are same suit."""
    if num_jokers == 0:
        # No jokers - check for natural flush house
        if len(set(real_suits)) == 1:  # All same suit
            rank_counts = {}
            for r in real_ranks:
                rank_counts[r] = rank_counts.get(r, 0) + 1
            return sorted(rank_counts.values()) == [2, 3]
        return False
    
    # With jokers - check if we can form full house pattern all same suit
    if len(set(real_suits)) <= 1:  # All real cards same suit (or no real cards)
        rank_counts = {}
        for r in real_ranks:
            rank_counts[r] = rank_counts.get(r, 0) + 1
        
        # Try to use jokers to complete 3+2 pattern
        ranks = list(rank_counts.keys())
        jokers_left = num_jokers
        
        if len(ranks) == 0:
            return jokers_left == 5  # All jokers can form flush house
        elif len(ranks) == 1:
            # One rank - try to make it triple and create pair with jokers
            count = rank_counts[ranks[0]]
            if count + jokers_left >= 3:
                jokers_used = max(0, 3 - count)
                return (jokers_left - jokers_used) >= 2
        elif len(ranks) >= 2:
            # Multiple ranks - try different 3+2 combinations
            for triple_rank in ranks:
                for pair_rank in ranks:
                    if triple_rank != pair_rank:
                        triple_count = rank_counts[triple_rank]
                        pair_count = rank_counts[pair_rank]
                        jokers_needed = max(0, 3 - triple_count) + max(0, 2 - pair_count)
                        if jokers_needed <= jokers_left:
                            return True
    return False

def _check_skipping_straight_with_jokers(real_ranks: List[int], num_jokers: int) -> bool:
    """Check for skipping straight: 5 cards skipping every other rank (2-4-6-8-10)."""
    if num_jokers == 0:
        # No jokers - check natural skipping straight
        if len(real_ranks) != 5:
            return False
        sorted_ranks = sorted(real_ranks)
        return all(sorted_ranks[i+1] - sorted_ranks[i] == 2 for i in range(4))
    
    # With jokers - try to complete skipping straight
    sorted_ranks = sorted(set(real_ranks))
    
    # Try different starting points for skipping sequence
    for start_rank in range(2, 15):
        if start_rank % 2 != sorted_ranks[0] % 2:  # Must maintain even/odd pattern
            continue
            
        # Generate target skipping sequence
        target_sequence = [start_rank + i*2 for i in range(5)]
        if any(r > 14 for r in target_sequence):  # Invalid high ranks
            continue
            
        # Check if real ranks + jokers can match this sequence
        matched = 0
        for target_rank in target_sequence:
            if target_rank in real_ranks:
                matched += 1
        
        if matched + num_jokers >= 5 and matched == len(real_ranks):
            return True
    
    return False

def _check_even_straight_with_jokers(real_ranks: List[int], num_jokers: int) -> bool:
    """Check for even straight: 5 consecutive even ranks (2-4-6-8-10)."""
    if num_jokers == 0:
        # No jokers - check natural even straight
        if len(real_ranks) != 5:
            return False
        sorted_ranks = sorted(real_ranks)
        return (all(r % 2 == 0 for r in sorted_ranks) and 
                all(sorted_ranks[i+1] - sorted_ranks[i] == 2 for i in range(4)))
    
    # With jokers - check if real cards are all even and can form sequence
    if not all(r % 2 == 0 for r in real_ranks):
        return False
        
    sorted_ranks = sorted(set(real_ranks))
    
    # Try different starting even ranks
    for start_rank in range(2, 11, 2):  # 2,4,6,8,10
        target_sequence = [start_rank + i*2 for i in range(5)]
        if target_sequence[-1] > 14:  # Don't exceed Ace
            continue
            
        matched = sum(1 for rank in target_sequence if rank in real_ranks)
        if matched + num_jokers >= 5 and matched == len(real_ranks):
            return True
    
    return False

def _check_odd_straight_with_jokers(real_ranks: List[int], num_jokers: int) -> bool:
    """Check for odd straight: 5 consecutive odd ranks (3-5-7-9-J)."""
    if num_jokers == 0:
        # No jokers - check natural odd straight  
        if len(real_ranks) != 5:
            return False
        sorted_ranks = sorted(real_ranks)
        return (all(r % 2 == 1 for r in sorted_ranks) and
                all(sorted_ranks[i+1] - sorted_ranks[i] == 2 for i in range(4)))
    
    # With jokers - check if real cards are all odd and can form sequence
    if not all(r % 2 == 1 for r in real_ranks):
        return False
        
    sorted_ranks = sorted(set(real_ranks))
    
    # Try different starting odd ranks (3,5,7,9,11)
    for start_rank in range(3, 12, 2):
        target_sequence = [start_rank + i*2 for i in range(5)]
        if target_sequence[-1] > 13:  # Don't exceed King (13)
            continue
            
        matched = sum(1 for rank in target_sequence if rank in real_ranks)
        if matched + num_jokers >= 5 and matched == len(real_ranks):
            return True
    
    return False

def _check_sandwich_hand_with_jokers(real_ranks: List[int], num_jokers: int) -> bool:
    """Check for sandwich hand: three-of-a-kind + two outer cards completing straight."""
    if num_jokers == 0:
        # No jokers - check natural sandwich hand
        rank_counts = {}
        for r in real_ranks:
            rank_counts[r] = rank_counts.get(r, 0) + 1
            
        if 3 not in rank_counts.values():
            return False
            
        # Find the triple
        triple_rank = [rank for rank, count in rank_counts.items() if count == 3][0]
        other_ranks = [rank for rank, count in rank_counts.items() if count != 3]
        
        if len(other_ranks) != 2:
            return False
            
        # Check if triple + other two cards form a straight pattern
        all_ranks = sorted([triple_rank] + other_ranks)
        return all(all_ranks[i+1] - all_ranks[i] == 1 for i in range(2))
    
    # With jokers - try to form sandwich pattern
    rank_counts = {}
    for r in real_ranks:
        rank_counts[r] = rank_counts.get(r, 0) + 1
    
    # Try using jokers to complete different sandwich patterns
    for triple_rank in range(2, 15):
        current_count = rank_counts.get(triple_rank, 0)
        jokers_for_triple = max(0, 3 - current_count)
        
        if jokers_for_triple > num_jokers:
            continue
            
        remaining_jokers = num_jokers - jokers_for_triple
        
        # Try different straight patterns around the triple
        for offset in range(-2, 3):  # Triple can be at different positions in straight
            if offset == 0:
                continue  # Skip the triple position
                
            straight_ranks = [triple_rank + i for i in range(-1, 2) if i != 0]  # Adjacent ranks
            needed_ranks = []
            
            for rank in straight_ranks:
                if rank < 2 or rank > 14:  # Invalid rank
                    break
                if rank_counts.get(rank, 0) == 0:  # Need joker for this rank
                    needed_ranks.append(rank)
            
            if len(needed_ranks) <= remaining_jokers:
                return True
    
    return False

# Hand ranking order
HAND_RANK_ORDER = [
    "High Card",           # Weakest
    "One Pair",           # Standard poker
    "Two Pair",           # Standard poker  
    "Three of a Kind",    # Standard poker
    "Straight",           # Standard poker
    "Flush",              # Standard poker
    "Full House",         # Standard poker
    "Four of a Kind",     # Standard poker
    "Straight Flush",     # Standard poker
    "Royal Flush",        # Standard poker
    "Flush Four",         # Weakest illegal/exotic hand
    "Sandwich Hand",      # Slightly stronger than Flush Four
    "Odd Straight",       # Exotic
    "Even Straight",      # Exotic
    "Skipping Straight",  # Very rare exotic
    "Rainbow Straight",   # Rare-ish, visually striking
    "Flush House",        # Rare
    "Five of a Kind",     # Uncommon but powerful
    "Flush Five"          # Ultra rare, strongest hand
]

# -----------------------------
# Decks and Players
# -----------------------------
real_deck = [f"{rank}{suit}" for rank in list(range(2, 11)) + ["J","Q","K","A"] for suit in ['♠','♥','♦','♣']] + ["JOKER", "JOKER"]

mod_deck = [
    ModCard(name="Extra Draw", description="Draw 1 card", effect="Draw1", type="player", flavorType="Pawn", rarity="Common"),
    ModCard(name="Sneaky Swap", description="Swap a card with opponent", effect="SwapCard", type="player", flavorType="Pawn", rarity="Uncommon"),
    ModCard(name="Royal Dividend", description="Gain +3 chips", effect="GainChips", type="payout", flavorType="Queen", rarity="Uncommon")
]

players = [
    PlayerCharacterCard(name="Scruffy McMuffins", char_class="Rogue", deck_modifier="Normal", ability="Steal 1 opponent card 2x per round"),
    PlayerCharacterCard(name="Patches", char_class="Pauper", deck_modifier="Remove face cards", ability="Blind money refunded"),
    PlayerCharacterCard(name="Sir Whiskers", char_class="Knight", deck_modifier="Normal", ability="Reveal opponent card once per round")
]

# Initialize chips and points
chips = {p.name: p.starting_chips for p in players}
points = {p.name: 0 for p in players}

# -----------------------------
# Simulation
# -----------------------------
num_rounds = 3
hand_size = 8

# round loop
for rnd in range(1, num_rounds+1):
    print(f"\n--- Round {rnd} ---")
    current_real_deck = real_deck.copy()
    random.shuffle(current_real_deck)
    current_mod_deck = mod_deck.copy()
    random.shuffle(current_mod_deck)
    
    all_player_hands = {}
    player_mods_in_hand = {}
    
    # Deal hands ONCE to all players
    for player in players:
        num_real = min(random.randint(5, hand_size), len(current_real_deck))
        player_real_cards = [current_real_deck.pop() for _ in range(num_real)]

        num_mod = max(0, hand_size - len(player_real_cards))
        num_mod = min(num_mod, len(current_mod_deck))
        player_mod_cards = [current_mod_deck.pop() for _ in range(num_mod)] if num_mod > 0 else []
        player_mods_in_hand[player.name] = player_mod_cards
        
        print(f"{player.name} hand:")
        print(" Real cards:", player_real_cards)
        print(" Mod cards:", [m.name for m in player_mod_cards])
        
        # Store hands for later access
        all_player_hands[player.name] = player_real_cards

    # Apply mod effects that don't require other players' hands
    for player in players:
        player_real_cards = all_player_hands[player.name]
        
        for mod in player_mods_in_hand[player.name]:
            if mod.effect == "Draw1" and current_real_deck:
                drawn = current_real_deck.pop()
                player_real_cards.append(drawn)
                print(f"  -> {player.name} draws extra card due to {mod.name}")

    # Apply mod effects that require access to other players' hands (like SwapCard)
    for player in players:
        player_real_cards = all_player_hands[player.name]
        
        for mod in player_mods_in_hand[player.name]:
            if mod.effect == "SwapCard":
                target = random.choice([p for p in players if p.name != player.name])
                target_hand = all_player_hands[target.name]
                
                if player_real_cards and target_hand:
                    my_card = player_real_cards.pop(random.randint(0, len(player_real_cards)-1))
                    their_card = target_hand.pop(random.randint(0, len(target_hand)-1))
                    
                    player_real_cards.append(their_card)
                    target_hand.append(my_card)
                    
                    print(f"  -> {player.name} swaps {my_card} with {target.name}'s {their_card}")

    # Apply character abilities
    round_abilities_used = {}  # Track ability usage per round
    
    for player in players:
        player_name = player.name
        player_real_cards = all_player_hands[player_name]
        
        # Rogue ability: Steal 1 opponent card 2x per round
        if player.char_class == "Rogue":
            steals_used = round_abilities_used.get(f"{player_name}_steals", 0)
            
            # Perform up to 2 steals per round
            while steals_used < 2:
                # Choose random opponent with cards
                targets = [p for p in players if p.name != player_name and all_player_hands[p.name]]
                if not targets:
                    break  # No valid targets with cards
                    
                target = random.choice(targets)
                target_hand = all_player_hands[target.name]
                
                stolen_card = target_hand.pop(random.randint(0, len(target_hand)-1))
                player_real_cards.append(stolen_card)
                steals_used += 1
                round_abilities_used[f"{player_name}_steals"] = steals_used
                print(f"  -> {player_name} (Rogue) steals {stolen_card} from {target.name} (steal #{steals_used})")
        
        # Knight ability: Reveal opponent card once per round
        elif player.char_class == "Knight":
            if not round_abilities_used.get(f"{player_name}_reveal_used", False):
                targets = [p for p in players if p.name != player_name]
                if targets:
                    target = random.choice(targets)
                    target_hand = all_player_hands[target.name]
                    
                    if target_hand:
                        revealed_card = random.choice(target_hand)
                        round_abilities_used[f"{player_name}_reveal_used"] = True
                        print(f"  -> {player_name} (Knight) reveals {target.name}'s {revealed_card}")
        
        # Pauper ability will be handled during payout (blind money refunded)

    # Handle burn effects - find mods to burn by matching properties
    for player in players:
        for mod in player_mods_in_hand[player.name]:
            if mod.burnOnUse:
                # Find matching mod in master deck by properties
                for deck_mod in mod_deck[:]:  # Create copy to iterate safely
                    if (deck_mod.name == mod.name and 
                        deck_mod.effect == mod.effect and 
                        deck_mod.burnOnUse == mod.burnOnUse):
                        mod_deck.remove(deck_mod)
                        print(f"  -> {mod.name} burned from deck")
                        break

    # Evaluate hands
    player_hands = {}
    for player in players:
        player_real_cards = all_player_hands[player.name]
        
        best_hand_type = "High Card"
        if len(player_real_cards) >= 5:
            for combo in combinations(player_real_cards, 5):
                # First check for illegal/exotic hands
                exotic_hand = evaluate_illegal_exotic(list(combo))
                
                # If no exotic hand found, check standard poker hands
                if exotic_hand == "High Card":
                    standard_hand = evaluate_standard_poker(list(combo))
                    hand_type = standard_hand
                else:
                    hand_type = exotic_hand
                
                # Keep the highest ranking hand
                if HAND_RANK_ORDER.index(hand_type) > HAND_RANK_ORDER.index(best_hand_type):
                    best_hand_type = hand_type
                    
        player_hands[player.name] = best_hand_type
        print(f"{player.name} best 5-card hand type:", best_hand_type)
    
    # Determine winner
    winner = max(player_hands, key=lambda x: HAND_RANK_ORDER.index(player_hands[x]))
    print("Winner of round:", winner)
    
    # Update points based on design document
    winner_hand = player_hands[winner]
    
    if winner_hand in ["Flush Five", "Five of a Kind"]:
        points[winner] += 2
        print(f"  -> {winner} gets 2 points for high-tier hand: {winner_hand}")
    else:
        points[winner] += 1
        print(f"  -> {winner} gets 1 point for: {winner_hand}")
    
    # Apply payout mods
    payout_burned_mods = []
    for mod in player_mods_in_hand[winner]:
        if mod.effect == "GainChips":
            chips[winner] += 3
            print(f"  -> {winner} gains 3 chips due to {mod.name}")
            if mod.burnOnUse:
                payout_burned_mods.append(mod)
    
    # Remove payout burned mods from the master deck
    for mod in payout_burned_mods:
        # Find matching mod in master deck by properties since objects differ
        for deck_mod in mod_deck[:]:  # Create copy to iterate safely
            if (deck_mod.name == mod.name and 
                deck_mod.effect == mod.effect and 
                deck_mod.burnOnUse == mod.burnOnUse):
                mod_deck.remove(deck_mod)
                break

    # Apply character-specific payout abilities
    for player in players:
        if player.char_class == "Pauper" and player.name != winner:
            # Pauper gets blind money refunded (small compensation for losing)
            chips[player.name] += 1
            print(f"  -> {player.name} (Pauper) gets 1 chip blind money refund")

# -----------------------------
# End simulation results
# -----------------------------
print("\n--- Final Points ---")
for player, pts in points.items():
    print(f"{player}: {pts} points")
    
print("\n--- Final Chips ---")
for player, ch in chips.items():
    print(f"{player}: {ch} chips")