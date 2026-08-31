import random


MOVES = ["R", "L", "U", "D", "F", "B"]
MODIFIERS = ["", "'", "2"]


def generate_scramble(length: int = 20) -> str:
    scramble = []
    previous_move = None

    while len(scramble) < length:
        move = random.choice(MOVES)

        if move == previous_move:
            continue

        modifier = random.choice(MODIFIERS)

        scramble.append(move + modifier)
        previous_move = move

    return " ".join(scramble)