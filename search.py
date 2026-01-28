from wikipedia_api import get_forward_links, get_backward_links, article_exists

MAX_DEPTH = 3


def find_path(start: str, end: str) -> dict:
    """Find the shortest chain of Wikipedia links between two articles."""

    if start == end:
        return {"success": True, "path": [start], "message": "Start and end are the same article"}

    if not article_exists(start):
        return {"success": False, "path": None, "message": f"Article not found: {start}"}
    if not article_exists(end):
        return {"success": False, "path": None, "message": f"Article not found: {end}"}

    forward_visited = {start}
    forward_parents = {start: None}
    forward_frontier = {start}

    backward_visited = {end}
    backward_parents = {end: None}
    backward_frontier = {end}

    for _ in range(MAX_DEPTH):
        # --- expand forward frontier ---
        new_forward = set()
        for title in forward_frontier:
            try:
                links = get_forward_links(title)
            except Exception:
                continue
            for link in links:
                if link not in forward_visited:
                    forward_visited.add(link)
                    forward_parents[link] = title
                    new_forward.add(link)
        forward_frontier = new_forward

        # check intersection
        meeting = forward_visited & backward_visited
        if meeting:
            return _build_result(meeting, forward_parents, backward_parents)

        # --- expand backward frontier ---
        new_backward = set()
        for title in backward_frontier:
            try:
                links = get_backward_links(title)
            except Exception:
                continue
            for link in links:
                if link not in backward_visited:
                    backward_visited.add(link)
                    backward_parents[link] = title
                    new_backward.add(link)
        backward_frontier = new_backward

        # check intersection
        meeting = forward_visited & backward_visited
        if meeting:
            return _build_result(meeting, forward_parents, backward_parents)

    return {"success": False, "path": None, "message": "No path found within depth limit"}


def _build_result(meeting: set, forward_parents: dict, backward_parents: dict) -> dict:
    """Pick the meeting point that gives the shortest path and return a result dict."""
    best_path = None
    for point in meeting:
        path = _reconstruct(point, forward_parents, backward_parents)
        if best_path is None or len(path) < len(best_path):
            best_path = path
    return {
        "success": True,
        "path": best_path,
        "message": f"Found path of length {len(best_path)}",
    }


def _reconstruct(meeting: str, forward_parents: dict, backward_parents: dict) -> list[str]:
    """Reconstruct the full path through the meeting point."""
    # walk from meeting point back to start
    forward_half = []
    node = meeting
    while node is not None:
        forward_half.append(node)
        node = forward_parents[node]
    forward_half.reverse()

    # walk from meeting point forward to end
    backward_half = []
    node = backward_parents[meeting]
    while node is not None:
        backward_half.append(node)
        node = backward_parents[node]

    return forward_half + backward_half
