# Tile type constants
FOREST, PLAINS, TOWER, CAVE, MOUNTAIN, WIZARD, BARBARIAN, DOMAIN = range(8)

# Owner constants
NONE, PLAYER, AI = 0, 1, 2

# Tile weights for random board generation (Domain placed deterministically)
TILE_WEIGHTS = {
    FOREST: 35,
    PLAINS: 20,
    TOWER: 8,
    CAVE: 8,
    MOUNTAIN: 15,
    WIZARD: 5,
    BARBARIAN: 9,
}

# Vision range per tile type
VISION_RANGE = {
    FOREST: 1,
    PLAINS: 2,
    TOWER: 3,
    CAVE: 1,
    MOUNTAIN: 0,
    WIZARD: 1,
    BARBARIAN: 1,
    DOMAIN: 1,
}

# AI strategic value per tile type
STRATEGIC_VALUE = {
    CAVE: 4,
    WIZARD: 3,
    TOWER: 2.5,
    PLAINS: 2,
    FOREST: 1.5,
    DOMAIN: 1.5,
    BARBARIAN: 0.5,
    MOUNTAIN: 0,
}

# Base hex color per tile type (for canvas rendering)
TILE_BASE_COLOR = {
    FOREST: '#2d4a2d',
    PLAINS: '#4a7a2a',
    TOWER: '#4a4a6a',
    CAVE: '#3a2a1a',
    MOUNTAIN: '#5a5a5a',
    WIZARD: '#3a1a5a',
    BARBARIAN: '#6a1a1a',
    DOMAIN: '#5a4a1a',
}

# Unicode icons per tile type
TILE_ICON = {
    FOREST: '♣',
    PLAINS: '≈',
    TOWER: '▲',
    CAVE: '○',
    MOUNTAIN: '◆',
    WIZARD: '✦',
    BARBARIAN: '⚔',
    DOMAIN: '⬡',
}

# Display names per tile type
TILE_LABEL = {
    FOREST: 'Forest',
    PLAINS: 'Plains',
    TOWER: 'Tower',
    CAVE: 'Cave',
    MOUNTAIN: 'Mountain',
    WIZARD: 'Wizard',
    BARBARIAN: 'Barbarian',
    DOMAIN: 'Domain',
}

# Cardinal directions: (dx, dy)
DIRS = [(0, -1), (0, 1), (-1, 0), (1, 0)]
