def adjacent(c1, c2):
    keyboard = [
        "qwertyuiop",
        "asdfghjkl",
        "zxcvbnm"
    ]
    
    def get_pos(c):
        c = c.lower()
        for row_idx, row in enumerate(keyboard):
            if c in row:
                col_idx = row.index(c)
                return (row_idx, col_idx)
        return None
    
    pos1 = get_pos(c1)
    pos2 = get_pos(c2)
    
    if pos1 is None or pos2 is None:
        return False
    
    row_dist = abs(pos1[0] - pos2[0])
    col_dist = abs(pos1[1] - pos2[1])
    
    return row_dist <= 1 and col_dist <= 1


def sub_cost(a, b):
    if a.lower() == b.lower() and a != b:
        return 0.5
    elif adjacent(a, b):
        return 1
    else:
        return 2


def del_cost(a, b_char=None):
    if b_char is None:
        return 1
    elif adjacent(a, b_char):
        return 1
    else:
        return 2


def print_table(table, a, b):
    # header row with b's characters
    header = "      " + "  ".join(f"{c:>4}" for c in [""] + list(b))
    print(header)
    print()

    for r, row in enumerate(table):
        # label each row with a's characters, first row is empty string
        row_label = a[r-1] if r > 0 else ""
        row_str = f"{row_label:>4}  " + "  ".join(f"{v:>4}" for v in row)
        print(row_str)
    print()


def edit_distance(a, b, debug=False):
    rows = len(a) + 1
    cols = len(b) + 1
    table = [[0] * cols for _ in range(rows)]

    # base cases
    for c in range(cols):
        table[0][c] = c * 3
    for r in range(rows):
        table[r][0] = r * 1

    for r in range(1, rows):
        for c in range(1, cols):
            if a[r-1] == b[c-1]:
                table[r][c] = table[r-1][c-1]
            else:
                substitution = table[r-1][c-1] + sub_cost(a[r-1], b[c-1])
                deletion = table[r-1][c] + del_cost(a[r-1], b[c-1])
                insertion = table[r][c-1] + 3
                table[r][c] = min(substitution, deletion, insertion)

    if debug:
        print_table(table, a, b)

    return table[rows-1][cols-1]


# some test cases
if __name__ == "__main__":
    test_cases = [
        ("love", "live"),
        ("love", "Love"),
        ("cat", "cat"),
        ("cat", ""),
        ("", "cat"),
        ("hello", "helo"),
        ("teh", "the"),
    ]

    for a, b in test_cases:
        dist = edit_distance(a, b, debug=True)
        print(f"edit_distance({a!r}, {b!r}) = {dist}")
        print("-" * 40)