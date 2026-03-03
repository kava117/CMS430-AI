from game.board import generate_board, idx, xy
from game.fog import compute_fog, bfs_reveal
from game.constants import CAVE, MOUNTAIN, DOMAIN, TOWER, PLAINS, NONE, PLAYER, AI


def _make_G(seed='fogtest', W=14, H=10):
    board = generate_board(seed, W, H)
    G = {'W': W, 'H': H, 'board': board, 'fog': set()}
    G['fog'] = compute_fog(G)
    return G


def test_starting_tiles_revealed():
    G = _make_G()
    player_idx = next(i for i, c in enumerate(G['board']) if c['owner'] == PLAYER)
    ai_idx     = next(i for i, c in enumerate(G['board']) if c['owner'] == AI)
    assert player_idx in G['fog']
    assert ai_idx in G['fog']


def test_cardinal_neighbor_of_domain_revealed():
    G = _make_G()
    player_idx = next(i for i, c in enumerate(G['board']) if c['owner'] == PLAYER)
    x, y = xy(player_idx, G['W'])
    neighbors = [
        idx(x+dx, y+dy, G['W'])
        for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]
        if 0 <= x+dx < G['W'] and 0 <= y+dy < G['H']
    ]
    assert any(n in G['fog'] for n in neighbors), "No neighbor of player domain revealed"


def test_fog_is_nonempty():
    G = _make_G()
    assert len(G['fog']) > 0


def test_mountain_does_not_block_bfs():
    # Mountains should not stop BFS propagation — tiles beyond them are still reachable
    W, H = 10, 8
    board = generate_board('bfstest', W, H)
    # Force a Mountain adjacent to start and check that tile beyond it can be revealed
    start = idx(1, 1, W)
    board[start]['owner'] = PLAYER
    mountain_idx = idx(2, 1, W)
    board[mountain_idx]['type'] = MOUNTAIN
    beyond_idx = idx(3, 1, W)
    G = {'W': W, 'H': H, 'board': board, 'fog': set()}
    G['fog'] = compute_fog(G)
    # Tower vision (range 3) would reveal beyond; Domain only range 1 so check range manually
    revealed = bfs_reveal(board, W, H, start, 3)
    assert beyond_idx in revealed, "BFS blocked by Mountain — should propagate through"


def test_cave_ownership_reveals_all_caves():
    W, H = 14, 10
    board = generate_board('cavetest', W, H)
    cave_indices = [i for i, c in enumerate(board) if c['type'] == CAVE]
    assert len(cave_indices) >= 2
    # Give player the first cave
    board[cave_indices[0]]['owner'] = PLAYER
    G = {'W': W, 'H': H, 'board': board, 'fog': set()}
    G['fog'] = compute_fog(G)
    for ci in cave_indices:
        assert ci in G['fog'], f"Cave at index {ci} not revealed globally"
