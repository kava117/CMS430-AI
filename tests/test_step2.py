"""Step 2 tests — press_button and state representation."""
import lightsout


def test_initial_state_2x2():
    """make_initial_state(2) should return a 2x2 grid of all True."""
    state = lightsout.make_initial_state(2)
    assert state == ((True, True), (True, True))


def test_initial_state_3x3():
    """make_initial_state(3) should return a 3x3 grid of all True."""
    state = lightsout.make_initial_state(3)
    assert len(state) == 3
    assert all(len(row) == 3 for row in state)
    assert all(cell is True for row in state for cell in row)


def test_state_is_immutable():
    """State should be a tuple of tuples."""
    state = lightsout.make_initial_state(3)
    assert isinstance(state, tuple)
    assert all(isinstance(row, tuple) for row in state)


def test_press_center_3x3():
    """Pressing center of 3x3 toggles center and 4 neighbors."""
    state = lightsout.make_initial_state(3)
    new_state = lightsout.press_button(state, 1, 1, 3)
    # Center and 4 neighbors should be False, corners stay True
    assert new_state[1][1] is False  # center
    assert new_state[0][1] is False  # up
    assert new_state[2][1] is False  # down
    assert new_state[1][0] is False  # left
    assert new_state[1][2] is False  # right
    # Corners unchanged
    assert new_state[0][0] is True
    assert new_state[0][2] is True
    assert new_state[2][0] is True
    assert new_state[2][2] is True


def test_press_corner_3x3():
    """Pressing top-left corner of 3x3 toggles 3 cells."""
    state = lightsout.make_initial_state(3)
    new_state = lightsout.press_button(state, 0, 0, 3)
    assert new_state[0][0] is False  # itself
    assert new_state[0][1] is False  # right neighbor
    assert new_state[1][0] is False  # down neighbor
    # Non-neighbors unchanged
    assert new_state[1][1] is True
    assert new_state[2][2] is True


def test_press_edge_3x3():
    """Pressing top-center of 3x3 toggles 4 cells (no up neighbor)."""
    state = lightsout.make_initial_state(3)
    new_state = lightsout.press_button(state, 0, 1, 3)
    assert new_state[0][1] is False  # itself
    assert new_state[0][0] is False  # left
    assert new_state[0][2] is False  # right
    assert new_state[1][1] is False  # down
    # No up neighbor — rest unchanged
    assert new_state[1][0] is True
    assert new_state[2][1] is True


def test_press_bottom_right_corner_2x2():
    """Pressing (1,1) on 2x2 toggles 3 cells."""
    state = lightsout.make_initial_state(2)
    new_state = lightsout.press_button(state, 1, 1, 2)
    assert new_state[1][1] is False  # itself
    assert new_state[0][1] is False  # up
    assert new_state[1][0] is False  # left
    # Top-left unchanged
    assert new_state[0][0] is True


def test_double_press_restores_state():
    """Pressing the same button twice should restore the original state."""
    state = lightsout.make_initial_state(3)
    once = lightsout.press_button(state, 1, 1, 3)
    twice = lightsout.press_button(once, 1, 1, 3)
    assert twice == state


def test_press_does_not_mutate_original():
    """press_button should return a new state, not mutate the original."""
    state = lightsout.make_initial_state(3)
    original = state
    lightsout.press_button(state, 1, 1, 3)
    assert state == original


def test_press_1x1():
    """Pressing the only button on a 1x1 grid toggles just that cell."""
    state = ((True,),)
    new_state = lightsout.press_button(state, 0, 0, 1)
    assert new_state == ((False,),)
