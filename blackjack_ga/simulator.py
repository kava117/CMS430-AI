import random
import numpy as np
from chromosome import get_decision


def make_deck() -> list:
    """Return an unshuffled standard 52-card deck."""
    # Four each of 1(Ace), 2-9, and 10 (covers 10/J/Q/K)
    return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10] * 4


def hand_value(cards: list) -> tuple:
    """
    Return (total, is_soft) for a list of card values.
    is_soft is True when at least one ace is counted as 11.
    """
    aces = sum(1 for c in cards if c == 1)
    total = sum(c for c in cards if c != 1) + aces  # all aces start as 1
    is_soft = False
    # Upgrade exactly one ace from 1 to 11 if it doesn't bust
    if aces > 0 and total + 10 <= 21:
        total += 10
        is_soft = True
    return total, is_soft


def simulate_hand(chrom: np.ndarray, deck: list) -> str:
    """
    Simulate one hand using the given chromosome and a pre-shuffled deck.
    Returns 'win', 'loss', or 'tie'.
    Draws cards sequentially from the front of the deck list.
    """
    idx = 0

    def draw():
        nonlocal idx
        card = deck[idx]
        idx += 1
        return card

    # Deal: p1, d_hole, p2, d_upcard
    p1 = draw()
    d_hole = draw()
    p2 = draw()
    d_upcard = draw()

    player_cards = [p1, p2]
    dealer_cards = [d_hole, d_upcard]

    player_total, player_soft = hand_value(player_cards)
    dealer_total, dealer_soft = hand_value(dealer_cards)

    # Check naturals
    player_natural = (player_total == 21 and len(player_cards) == 2)
    dealer_natural = (dealer_total == 21 and len(dealer_cards) == 2)
    if player_natural or dealer_natural:
        if player_natural and dealer_natural:
            return 'tie'
        if player_natural:
            return 'win'
        return 'loss'

    # Player loop
    while player_total < 21:
        decision = get_decision(chrom, player_total, player_soft, d_upcard)
        if decision == 0:  # stand
            break
        player_cards.append(draw())
        player_total, player_soft = hand_value(player_cards)

    if player_total > 21:
        return 'loss'

    # Dealer loop: stands on 17+
    while dealer_total < 17:
        dealer_cards.append(draw())
        dealer_total, dealer_soft = hand_value(dealer_cards)

    if dealer_total > 21:
        return 'win'

    if player_total > dealer_total:
        return 'win'
    if player_total < dealer_total:
        return 'loss'
    return 'tie'


def evaluate_fitness(chrom: np.ndarray, n_hands: int = 1000) -> float:
    """
    Simulate n_hands of blackjack using the given strategy chromosome.
    Returns fitness = (wins + 0.5 * ties) / n_hands.
    """
    wins = 0
    ties = 0
    for _ in range(n_hands):
        deck = make_deck()
        random.shuffle(deck)
        result = simulate_hand(chrom, deck)
        if result == 'win':
            wins += 1
        elif result == 'tie':
            ties += 1
    return (wins + 0.5 * ties) / n_hands
