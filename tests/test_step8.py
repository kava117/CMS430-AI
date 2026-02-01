"""Step 8 tests — end-to-end integration and edge cases."""
import lightsout


class TestSolutionCorrectness:
    """Verify solutions are correct by applying them to the initial state."""

    def _verify_solution(self, n):
        """Helper: solve and verify for grid size n."""
        bfs_sol, _, _ = lightsout.solve_lights_out_bfs(n)
        iddfs_sol, _, _ = lightsout.solve_lights_out_iddfs(n)

        # Both should find a solution
        assert bfs_sol is not None, f"BFS failed for {n}x{n}"
        assert iddfs_sol is not None, f"IDDFS failed for {n}x{n}"

        # Verify BFS solution
        state = lightsout.make_initial_state(n)
        for row, col in bfs_sol:
            state = lightsout.press_button(state, row, col, n)
        assert lightsout.is_goal(state), f"BFS solution invalid for {n}x{n}"

        # Verify IDDFS solution
        state = lightsout.make_initial_state(n)
        for row, col in iddfs_sol:
            state = lightsout.press_button(state, row, col, n)
        assert lightsout.is_goal(state), f"IDDFS solution invalid for {n}x{n}"

    def test_1x1(self):
        self._verify_solution(1)

    def test_2x2(self):
        self._verify_solution(2)

    def test_3x3(self):
        self._verify_solution(3)

    def test_4x4(self):
        self._verify_solution(4)


class TestSolutionOptimality:
    """BFS and IDDFS should find solutions of the same length."""

    def test_2x2_same_length(self):
        bfs_sol, _, _ = lightsout.solve_lights_out_bfs(2)
        iddfs_sol, _, _ = lightsout.solve_lights_out_iddfs(2)
        assert len(bfs_sol) == len(iddfs_sol)

    def test_3x3_same_length(self):
        bfs_sol, _, _ = lightsout.solve_lights_out_bfs(3)
        iddfs_sol, _, _ = lightsout.solve_lights_out_iddfs(3)
        assert len(bfs_sol) == len(iddfs_sol)


class TestEdgeCases:
    def test_press_button_all_positions_3x3(self):
        """Pressing every button on a 3x3 grid should not crash."""
        state = lightsout.make_initial_state(3)
        for r in range(3):
            for c in range(3):
                state = lightsout.press_button(state, r, c, 3)
        # Just verify we get a valid state back
        assert len(state) == 3
        assert all(len(row) == 3 for row in state)

    def test_goal_state_as_input_to_successors(self):
        """get_successors should work on the goal state."""
        goal = ((False, False), (False, False))
        successors = lightsout.get_successors(goal, 2, frozenset())
        assert len(successors) == 4

    def test_solution_buttons_within_bounds(self):
        """All buttons in a solution should be within grid bounds."""
        for n in [2, 3]:
            solution, _, _ = lightsout.solve_lights_out_bfs(n)
            for row, col in solution:
                assert 0 <= row < n
                assert 0 <= col < n

    def test_no_repeated_buttons_in_solution(self):
        """Solutions should never press the same button twice."""
        for n in [2, 3]:
            bfs_sol, _, _ = lightsout.solve_lights_out_bfs(n)
            iddfs_sol, _, _ = lightsout.solve_lights_out_iddfs(n)
            assert len(bfs_sol) == len(set(bfs_sol))
            assert len(iddfs_sol) == len(set(iddfs_sol))


class TestReturnTypes:
    def test_bfs_return_type(self):
        solution, expanded, created = lightsout.solve_lights_out_bfs(2)
        assert isinstance(solution, tuple)
        assert isinstance(expanded, int)
        assert isinstance(created, int)

    def test_iddfs_return_type(self):
        solution, expanded, created = lightsout.solve_lights_out_iddfs(2)
        assert isinstance(solution, tuple)
        assert isinstance(expanded, int)
        assert isinstance(created, int)

    def test_compare_return_type(self):
        results = lightsout.compare_algorithms([2])
        assert isinstance(results, dict)
        assert isinstance(results["bfs_expanded"], list)
        assert isinstance(results["bfs_created"], list)
        assert isinstance(results["iddfs_expanded"], list)
        assert isinstance(results["iddfs_created"], list)
