# Assignment requirement mapping

| Requirement | Implementation |
|---|---|
| Library graph | `navigation.py` creates a five-floor shelf graph |
| Shelves and book locations as states | Nodes are floor/section/aisle/shelf combinations |
| Walking between sections as actions | Graph edges represent aisle, shelf and stair movement |
| BFS and DFS | `navigation.search` |
| A* with walking cost estimate | `navigation.search` with Manhattan-style heuristic |
| Closed sections | Sidebar control removes section connections |
| Unavailable books | The current source catalogue has no availability field; real status requires copy inventory data |
| Crowded aisles | Sidebar adds a +4 edge cost penalty |
| Restricted shelves | Sidebar restricts a shelf node |
| Open/closed lists and path cost | Single and multiple finder trace expanders |
| Graphical/web interface | Streamlit tabs |
| Multiple-book optimization | Multi-stop heuristic route planner with time budget |
