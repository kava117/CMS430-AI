"""Step 3 tests — is_goal and get_successors."""
import lightsout


def test_is_goal_all_off():
    """All-OFF grid should be the goal state."""
    state = ((False, False), (False, False))
    assert lightsout.is_goal(state) is True


def test_is_goal_all_on():
    """All-ON grid is not the goal state."""
    state = lightsout.make_initial_state(3)
    assert lightsout.is_goal(state) is False


def test_is_goal_one_on():
    """A grid with even one ON cell is not the goal."""
    state = ((False, False), (True, False))
    assert lightsout.is_goal(state) is False


def test_is_goal_1x1_off():
    """1x1 all-OFF is goal."""
    assert lightsout.is_goal(((False,),)) is True


def test_is_goal_1x1_on():
    """1x1 all-ON is not goal."""
    assert lightsout.is_goal(((True,),)) is False


def test_successors_count_no_pressed():
    """With no buttons pressed, successors should equal n*n."""
    state = lightsout.make_initial_state(2)
    successors = lightsout.get_successors(state, 2, frozenset())
    assert len(successors) == 4  # 2x2 = 4 buttons


def test_successors_count_some_pressed():
    """With some buttons pressed, successors should be fewer."""
    state = lightsout.make_initial_state(2)
    pressed = frozenset({(0, 0), (1, 1)})
    successors = lightsout.get_successors(state, 2, pressed)
    assert len(successors) == 2  # 4 - 2 pressed = 2 remaining


def test_successors_count_3x3():
    """3x3 grid with no pressed buttons should yield 9 successors."""
    state = lightsout.make_initial_state(3)
    successors = lightsout.get_successors(state, 3, frozenset())
    assert len(successors) == 9


def test_successor_tuple_structure():
    """Each successor should be (new_state, button, updated_pressed)."""
    state = lightsout.make_initial_state(2)
    successors = lightsout.get_successors(state, 2, frozenset())
    for new_state, button, new_pressed in successors:
        assert isinstance(new_state, tuple)
        assert isinstance(button, tuple)
        assert len(button) == 2
        assert button in new_pressed


def test_successor_state_differs():
    """Each successor's state should differ from the original."""
    state = lightsout.make_initial_state(2)
    successors = lightsout.get_successors(state, 2, frozenset())
    for new_state, button, new_pressed in successors:
        assert new_state != state


def test_successors_skip_pressed():
    """Buttons in the pressed set should not appear in successors."""
    state = lightsout.make_initial_state(2)
    pressed = frozenset({(0, 0)})
    successors = lightsout.get_successors(state, 2, pressed)
    buttons = [button for _, button, _ in successors]
    assert (0, 0) not in buttons


def test_successor_pressed_set_is_superset():
    """Updated pressed set should contain the original pressed set plus the new button."""
    state = lightsout.make_initial_state(2)
    original_pressed = frozenset({(0, 0)})
    successors = lightsout.get_successors(state, 2, original_pressed)
    for _, button, new_pressed in successors:
        assert original_pressed.issubset(new_pressed)
        assert button in new_pressed
