# Intelligent Library Search & Book Collection Agent

## Run on Windows
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m streamlit run app.py
```
If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` for that terminal, then activate again.

## Included features
- Imports the uploaded books CSV (271,360 usable records after malformed rows are skipped).
- Book Catalogue with title/author/ISBN search and filters.
- Single Book Finder with BFS, DFS and A*.
- Multiple Book Finder with BFS, DFS and A* route modes.
- Five-floor graph: five sections per floor, three aisles per section, four shelves per aisle.
- Shelf-level assigned floor, section, aisle, shelf, row and column.
- Closed sections, restricted shelf nodes and crowded-aisle cost penalties.
- Open/discovered list, closed/expanded list, route and path cost.

## Important data accuracy note
The uploaded CSV contains bibliographic metadata (ISBN, title, author, publication year, publisher and image URLs). It does **not** contain physical library copy IDs, availability, floor plans or shelf coordinates. Therefore, this starter assigns deterministic **simulated demo locations** to catalogue records so the assignment workflow can be demonstrated. Do not represent these as real-world shelf locations.

For real deployment, obtain an inventory export from the target library with one row per physical copy, ideally including:
`copy_id, isbn, barcode, status, floor, section, aisle, shelf, row, column`.
Use actual floor-plan connectivity and verify the mapping with library staff.

## Algorithm notes
- BFS explores by number of edges; it is optimal only when every edge has equal cost.
- DFS explores depth-first and does not guarantee a shortest route.
- A* uses an estimated walking-cost heuristic.
- Multi-book planning currently uses a heuristic ordering, not an exact globally optimal solution to the travelling-salesperson problem.

## CSV format
The provided catalogue is normalized to UTF-8 comma-separated CSV in `data/books.csv`. Original source was semicolon-separated and encoded in Windows-1252; malformed rows were skipped during import.
