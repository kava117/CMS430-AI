import random
import numpy as np
from chromosome import get_decision, get_count_values, get_bet_multipliers

SHOE_SIZE = 312          # 6 decks × 52 cards
PENETRATION = 234        # reshuffle when cards_dealt >= 234 (75%)
STARTING_BANKROLL = 1000.0


def make_shoe() -> list:
    """Return an unshuffled 6-deck shoe (312 cards)."""
    single_deck = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10] * 4
    return single_deck * 6


def hand_value(cards: list) -> tuple:
    """
    Return (total, is_soft) for a list of card values.
    All aces counted as 1 first; upgrade one ace to 11 if total stays <= 21.
    """
    total = sum(c if c != 1 else 1 for c in cards)
    num_aces = cards.count(1)
    is_soft = False
    if num_aces > 0 and total + 10 <= 21:
        total += 10
        is_soft = True
    return total, is_soft


def calculate_true_count(running_count: int, cards_dealt: int,
                         shoe_size: int = SHOE_SIZE) -> int:
    """True count = round(running_count / decks_remaining)."""
    decks_remaining = (shoe_size - cards_dealt) / 52
    if decks_remaining <= 0:
        return 0
    return round(running_count / decks_remaining)


def get_bet(chrom: np.ndarray, running_count: int, cards_dealt: int,
            bankroll: float) -> float:
    """
    Determine bet size based on true count and chromosome's bet multipliers.
    Base unit = $1. Bet is capped at bankroll.
    """
    tc = calculate_true_count(running_count, cards_dealt)
    multipliers = get_bet_multipliers(chrom)

    if tc <= -2:
        mult = multipliers[0]
    elif tc <= 1:
        mult = multipliers[1]
    elif tc <= 4:
        mult = multipliers[2]
    else:
        mult = multipliers[3]

    return min(float(mult), bankroll)


def simulate_hand(chrom: np.ndarray, shoe: list, cards_dealt: int,
                  running_count: int, bankroll: float,
                  bet: float) -> tuple:
    """
    Simulate one hand. Draws from shoe[cards_dealt:] using index pointer.
    Hole card count is added only when dealer reveals it.

    Returns: (outcome, cards_dealt, running_count, bankroll)
    """
    count_values = get_count_values(chrom)

    def draw():
        nonlocal cards_dealt
        card = shoe[cards_dealt]
        cards_dealt += 1
        return card

    def cv(card):
        """Count value for a card."""
        return count_values[min(card, 10)]

    # Deal initial 4 cards: p1, dealer_hole, p2, dealer_upcard
    p1 = draw()
    hole = draw()          # dealer hole card — count NOT added yet
    p2 = draw()
    upcard = draw()

    # Count the three revealed cards (not the hole)
    running_count += cv(p1) + cv(p2) + cv(upcard)

    player_cards = [p1, p2]
    dealer_cards = [hole, upcard]

    player_total, player_soft = hand_value(player_cards)
    dealer_upcard_val = min(upcard, 10)

    # Check for naturals
    player_bj = (player_total == 21 and len(player_cards) == 2)
    # Dealer natural check needs hole card
    dealer_total_initial, _ = hand_value(dealer_cards)
    dealer_bj = (dealer_total_initial == 21 and len(dealer_cards) == 2)

    if player_bj or dealer_bj:
        # Reveal hole card for counting
        running_count += cv(hole)
        if player_bj and dealer_bj:
            return ('tie', cards_dealt, running_count, bankroll)
        elif player_bj:
            bankroll += 1.5 * bet
            return ('win', cards_dealt, running_count, bankroll)
        else:
            bankroll -= bet
            return ('loss', cards_dealt, running_count, bankroll)

    # Player loop
    while player_total < 21:
        decision = get_decision(chrom, player_total, player_soft, dealer_upcard_val)
        if decision == 0:  # stand
            break
        card = draw()
        running_count += cv(card)
        player_cards.append(card)
        player_total, player_soft = hand_value(player_cards)

    if player_total > 21:
        # Player busts — reveal hole card for count purposes
        running_count += cv(hole)
        # Dealer doesn't play when player busts, but we still count upcard already done
        bankroll -= bet
        return ('loss', cards_dealt, running_count, bankroll)

    # Dealer loop — reveal hole card now
    running_count += cv(hole)
    dealer_total, dealer_soft = hand_value(dealer_cards)

    while dealer_total < 17:
        card = draw()
        running_count += cv(card)
        dealer_cards.append(card)
        dealer_total, dealer_soft = hand_value(dealer_cards)

    # Resolve
    if dealer_total > 21:
        outcome = 'win'
        bankroll += bet
    elif player_total > dealer_total:
        outcome = 'win'
        bankroll += bet
    elif player_total < dealer_total:
        outcome = 'loss'
        bankroll -= bet
    else:
        outcome = 'tie'

    return (outcome, cards_dealt, running_count, bankroll)


def simulate_session(chrom: np.ndarray, n_hands: int = 1000) -> list:
    """
    Simulate a full session. Returns bankroll after each hand (list of floats).
    Stops early if bankroll reaches 0.
    """
    shoe = make_shoe()
    random.shuffle(shoe)
    cards_dealt = 0
    running_count = 0
    bankroll = STARTING_BANKROLL
    history = []

    for _ in range(n_hands):
        # Reshuffle if penetration threshold reached
        if cards_dealt >= PENETRATION:
            random.shuffle(shoe)
            cards_dealt = 0
            running_count = 0

        if bankroll <= 0:
            break

        bet = get_bet(chrom, running_count, cards_dealt, bankroll)
        _, cards_dealt, running_count, bankroll = simulate_hand(
            chrom, shoe, cards_dealt, running_count, bankroll, bet
        )
        history.append(bankroll)

        if bankroll <= 0:
            break

    return history


def evaluate_fitness(chrom: np.ndarray, n_hands: int = 1000) -> float:
    """
    Simulate a session and return final bankroll as fitness.
    Returns 0.0 if bankroll hits 0 before n_hands complete.
    """
    history = simulate_session(chrom, n_hands)
    if not history:
        return 0.0
    return float(history[-1])
