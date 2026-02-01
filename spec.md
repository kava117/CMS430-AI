# Wikipedia Article Chain Finder - Project Specification

## Project Overview

Create a web application that finds the shortest chain of links between two Wikipedia articles using bidirectional iterative deepening search.

## Architecture

The application consists of three main components:

1. **Frontend**: HTML/CSS/Vanilla JavaScript interface
2. **Backend**: Python Flask API server
3. **Search Engine**: Bidirectional search implementation using the Wikimedia API

## Frontend Requirements

### Technology Stack
- HTML5
- CSS3
- Vanilla JavaScript (no frameworks)

### User Interface
The interface should include:
- Two labeled input boxes for article titles (start and end)
- A submit button to initiate the search
- A results area displaying:
  - Success: The article chain as clickable links to actual Wikipedia articles
  - Failure: Clear message explaining why no path was found
  - Errors: User-friendly error messages
- A loading indicator (spinner or progress message) while search is in progress

### Behavior
- Submit form data to the Flask API endpoint
- Display loading state during search
- Parse and display results
- Handle errors gracefully with user-friendly messages

## Backend Requirements

### Technology Stack
- Python 3.x
- Flask web framework

### API Design

#### Endpoint: Find Path
```
POST /api/find-path
Content-Type: application/json

Request Body:
{
  "start": "Article_Title",
  "end": "Article_Title"
}

Response Body (Success):
{
  "success": true,
  "path": ["Article1", "Article2", "Article3", ...],
  "message": "Found path of length N"
}

Response Body (Failure):
{
  "success": false,
  "path": null,
  "message": "No path found within depth limit" | "Invalid article title" | error description
}
```

#### Optional Endpoint: Health Check
```
GET /api/status

Response:
{
  "status": "ok"
}
```

### Flask Application Structure
- Serve static files (HTML/CSS/JS) from a `/static` directory
- Handle CORS if needed for local development
- Implement proper error handling and HTTP status codes
- Return appropriate status codes (200 for success, 404 for invalid articles, 500 for server errors)

## Search Algorithm Requirements

### Algorithm: Bidirectional Iterative Deepening Search

The search runs two simultaneous iterative deepening searches:
1. Forward search from the start article
2. Backward search from the end article

Both searches expand level by level, checking for intersection after each depth level is completed.

### Data Structures

Maintain the following for each direction:
- **Frontier**: Set of articles to explore at the current depth
- **Visited**: Set of all articles seen so far
- **Parents**: Dictionary mapping each article to its parent in the search tree
  - `forward_parents[article] = previous_article`
  - `backward_parents[article] = next_article`

### Search Termination

The search should terminate when:
1. **Success**: A node appears in both visited sets (searches meet in the middle)
2. **Failure**: Maximum depth is reached without finding intersection
3. **Error**: Invalid article, API errors, or other issues

### Depth Limit

- Maximum depth: **3 levels on each side**
- This allows paths up to **7 articles** long (start → 3 links → middle → 3 links → end)
- Return failure if no path is found within this limit

### Path Reconstruction

When searches meet at a common article:
1. Walk backward from meeting point to start using `forward_parents`
2. Walk forward from meeting point to end using `backward_parents`
3. Combine to form complete path: `[start, ..., meeting_point, ..., end]`

## Wikimedia API Integration

### API Endpoints to Use

#### Getting Forward Links (outgoing links from a page)
```
GET https://en.wikipedia.org/w/api.php
Parameters:
  action=query
  titles=Article_Title
  prop=links
  pllimit=max
  plnamespace=0
  format=json
```

#### Getting Backward Links (pages that link to this page)
```
GET https://en.wikipedia.org/w/api.php
Parameters:
  action=query
  titles=Article_Title
  prop=linkshere
  lhlimit=max
  lhnamespace=0
  format=json
```

### Link Filtering

- Only follow links in **namespace 0** (main article space)
- Exclude links to:
  - Admin/meta pages
  - Discussion/talk pages
  - User pages
  - File/Image pages
  - Wikipedia special pages
  - Category pages

### API Considerations

- Wikipedia article titles are case-sensitive for the first letter but case-insensitive afterward
- Handle URL encoding for article titles with special characters
- Handle redirects appropriately (the API typically resolves these)
- Be aware that popular articles may have thousands of backlinks

### Backlink Handling

For popular pages, the number of backlinks can be very large. For the first version:
- Accept potential slowness when dealing with popular pages
- Consider implementing a reasonable limit (e.g., first 500 backlinks) if performance becomes an issue
- This can be optimized in future versions

## Error Handling

### Article Validation
- Check if both start and end articles exist before beginning search
- Return clear error message if either article is invalid
- Handle case where start and end are the same article (return immediate success with single-article path)

### API Errors
- Network failures
- API rate limiting
- Malformed responses
- Timeout handling

### Edge Cases
- Articles with no outgoing links (dead ends)
- Articles with very few incoming links
- Disambiguation pages
- Very long article titles

## Implementation Guidelines

### Threading
- Single-threaded implementation is acceptable for the first version
- No need for parallel processing or async operations

### Caching

The application uses a SQLite-based cache to avoid redundant Wikipedia API calls for previously fetched links.

#### Database

- File: `links_cache.db` (created automatically on first use)
- Uses Python's built-in `sqlite3` module (no additional dependencies)

#### Schema

```sql
CREATE TABLE IF NOT EXISTS links (
    source TEXT NOT NULL,
    target TEXT NOT NULL,
    direction TEXT NOT NULL,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (source, target, direction)
);
CREATE INDEX IF NOT EXISTS idx_source_direction ON links(source, direction);
```

- `source`: the article whose links were fetched
- `target`: a linked article
- `direction`: `"forward"` or `"backward"`, so the two link types are stored independently
- `cached_at`: timestamp for potential future cache expiration

#### Cache API (`cache.py`)

| Function | Description |
|---|---|
| `init_db()` | Create the database and tables if they don't exist. Idempotent. |
| `get_cached_links(title, direction) -> set[str] \| None` | Return cached link titles, or `None` if the article has not been cached yet. An empty set is a valid cached result (distinguishable from `None`). |
| `cache_links(title, links, direction)` | Store a set of links for the given article and direction. |
| `clear_cache()` | Delete all rows from the cache table. |

#### Integration with Wikipedia API

- `get_forward_links()` checks the cache first. On a cache miss it fetches from the API, stores the result, then returns it.
- `get_backward_links()` behaves the same way.
- `article_exists()` is **not** cached (existence checks are cheap and should stay fresh).

### Code Organization

Suggested file structure:
```
project/
├── app.py                 # Flask application entry point
├── search.py              # Bidirectional search implementation
├── wikipedia_api.py       # Wikimedia API wrapper functions
├── cache.py               # SQLite caching layer for Wikipedia links
├── static/
│   ├── index.html        # Main HTML page
│   ├── style.css         # Styling
│   └── script.js         # Frontend JavaScript
└── requirements.txt       # Python dependencies
```

### Python Dependencies
Minimum requirements:
- Flask
- requests (for API calls)

## User Experience Considerations

### Loading States
- Show clear loading indicator when search is in progress
- Consider showing current search depth or progress (optional)

### Results Display
- Display the path as a numbered or arrow-separated list
- Make each article in the path a clickable link to the actual Wikipedia article
- Show the total path length
- For failures, explain clearly why no path was found

### Input Validation
- Trim whitespace from article titles
- Provide helpful error messages for empty inputs
- Handle special characters in article titles

## Testing Recommendations

### Test Cases
1. **Simple paths**: Articles that are closely connected (1-2 links apart)
2. **Medium paths**: Articles requiring 3-5 links
3. **Distant articles**: Articles at or beyond the depth limit
4. **Special cases**:
   - Same start and end article
   - Non-existent articles
   - Articles with very few links
   - Popular articles with many links
5. **Edge cases**:
   - Articles with special characters in titles
   - Very long article titles
   - Redirect articles

### Example Test Pairs
- **Close**: "Python (programming language)" → "Programming language" (likely 1 link)
- **Medium**: "Albert Einstein" → "Quantum mechanics" (likely 2-3 links)
- **Challenging**: "Ice cream" → "Philosophy" (may require deeper search)

## Performance Expectations

- Simple paths (1-2 links): < 5 seconds
- Medium paths (3-5 links): 5-30 seconds
- Complex searches near depth limit: 30-60 seconds

Note: Performance heavily depends on article popularity and API response times.

## Future Enhancements (Not Required for First Version)

- Cache expiration / TTL-based invalidation
- Pre-computed database of page relationships
- A* or other heuristic search algorithms
- Multi-threading for parallel frontier exploration
- Progress bar showing search status
- Search history
- Visualization of the search process
- Statistics (nodes explored, API calls made, time taken)

## Deliverables

1. Working Flask application with all endpoints
2. Frontend interface accessible via web browser
3. Bidirectional search implementation
4. README with setup and running instructions
5. requirements.txt with all dependencies

## Success Criteria

The project is successful when:
1. Users can input two Wikipedia article titles
2. The system finds a path between them (if one exists within depth limit)
3. Results are displayed as clickable links
4. Appropriate error messages are shown for failures
5. The application handles common edge cases gracefully