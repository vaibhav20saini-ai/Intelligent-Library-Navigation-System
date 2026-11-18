
import streamlit as st
import pandas as pd
import math

from navigation import (
    build_graph,
    node_id,
    search,
    plan_multiple,
    path_actions,
    SECTIONS
)

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Intelligent Library Navigation",
    page_icon="📚",
    layout="wide"
)

# =====================================================
# PROFESSIONAL LIGHT THEME
# =====================================================

st.markdown("""
<style>

/* Main application */
.stApp {
    background-color: #F8FAFC !important;
    color: #243B53 !important;
}

[data-testid="stAppViewContainer"] {
    background-color: #F8FAFC !important;
}

[data-testid="stMain"] {
    background-color: #F8FAFC !important;
}

/* Main content spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #EAF2F8 !important;
    border-right: 1px solid #D9E2EC;
}

[data-testid="stSidebar"] > div {
    background-color: #EAF2F8 !important;
}

/* Headings */
h1, h2, h3, h4 {
    color: #243B53 !important;
    font-weight: 700 !important;
}

/* General text */
p, label, .stMarkdown, li {
    color: #334E68;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: #334E68 !important;
    font-weight: 600 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #087E8B !important;
    border-bottom: 3px solid #087E8B !important;
}

/* Text input */
[data-baseweb="input"] > div {
    background-color: #FFFFFF !important;
    border: 1px solid #BCCCDC !important;
    border-radius: 8px !important;
}

[data-baseweb="input"] input {
    background-color: #FFFFFF !important;
    color: #243B53 !important;
}

/* Text area */
[data-baseweb="textarea"] {
    background-color: #FFFFFF !important;
    color: #243B53 !important;
}

/* Select boxes */
[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #243B53 !important;
    border: 1px solid #BCCCDC !important;
    border-radius: 8px !important;
}

/* Select box text */
[data-baseweb="select"] span {
    color: #243B53 !important;
}

/* Dropdown menu */
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"] {
    background-color: #FFFFFF !important;
}

[role="option"] {
    background-color: #FFFFFF !important;
    color: #243B53 !important;
}

[role="option"]:hover {
    background-color: #EAF2F8 !important;
}

/* Buttons */
.stButton button,
.stDownloadButton button {
    background-color: #087E8B !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 8px 18px !important;
}

.stButton button:hover,
.stDownloadButton button:hover {
    background-color: #066773 !important;
    color: #FFFFFF !important;
}

/* Radio buttons */
[data-testid="stRadio"] label {
    color: #243B53 !important;
}

/* Checkboxes */
[data-testid="stCheckbox"] label {
    color: #243B53 !important;
}

/* Multiselect */
[data-baseweb="tag"] {
    background-color: #D8EEF0 !important;
}

[data-baseweb="tag"] span {
    color: #075B65 !important;
}

/* Catalogue table */
[data-testid="stDataFrame"] {
    background-color: #FFFFFF !important;
    border: 1px solid #D9E2EC !important;
    border-radius: 9px !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background-color: #EAF2F8 !important;
    border: 1px solid #D9E2EC !important;
    border-radius: 10px !important;
    padding: 12px !important;
}

/* Expanders */
[data-testid="stExpander"] {
    background-color: #FFFFFF !important;
    border: 1px solid #D9E2EC !important;
    border-radius: 8px !important;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 8px !important;
}

/* Divider */
hr {
    border-color: #D9E2EC !important;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# MAIN HEADING
# =====================================================

st.title("📚 Intelligent Library Search & Navigation Agent")

# =====================================================
# LOAD BOOK CATALOGUE
# =====================================================

DATA_PATH = "data/books.csv"

@st.cache_data(show_spinner="Loading book catalogue...")
def load_books():

    df = pd.read_csv(
        DATA_PATH,
        dtype=str,
        keep_default_na=False
    )

    df = df.fillna("")

    for c in [
        "isbn",
        "title",
        "author",
        "year",
        "publisher",
        "image_url"
    ]:
        if c not in df:
            df[c] = ""

    df["title_clean"] = df["title"].str.strip()

    df = df[df["title_clean"] != ""].copy()

    df = df.reset_index(drop=True)

    df["record_id"] = df.index.astype(str)

    df["availability"] = df.index.map(
        lambda i: "Unavailable (demo)"
        if i % 37 == 0
        else "Available (demo)"
    )

    # Five-floor library locations
    df["floor"] = (df.index % 5) + 1

    df["section_no"] = (df.index // 5) % 5 + 1

    df["aisle"] = (df.index // 25) % 3 + 1

    df["shelf"] = (df.index // 75) % 4 + 1

    df["row"] = (df.index // 3) % 6 + 1

    df["column"] = (df.index % 3) + 1

    df["section"] = df["section_no"].map(
        lambda x: SECTIONS[x - 1]
    )

    df["node"] = df.apply(
        lambda r: node_id(
            int(r.floor),
            int(r.section_no),
            int(r.aisle),
            int(r.shelf)
        ),
        axis=1
    )

    return df

df = load_books()

# =====================================================
# SIDEBAR: LIBRARY CONTROLS
# =====================================================

st.sidebar.title("📚 Library Controls")

closed = st.sidebar.multiselect(
    "Closed sections",
    SECTIONS
)

crowded_choices = [
    f"Floor {f} · {SECTIONS[s-1]} · Aisle {a}"
    for f in range(1, 6)
    for s in range(1, 6)
    for a in range(1, 4)
]

crowded_selected = st.sidebar.multiselect(
    "Crowded aisles (+4 cost)",
    crowded_choices
)

restricted_text = st.sidebar.text_input(
    "Restricted shelf node",
    placeholder="F2-S1-A2-H3"
)

restricted = (
    [restricted_text.strip()]
    if restricted_text.strip()
    else []
)

crowded = set()

for item in crowded_selected:

    parts = item.replace("Floor ", "").split(" · ")

    f = int(parts[0])

    sec = parts[1]

    a = int(parts[2].replace("Aisle ", ""))

    crowded.add(
        (f, SECTIONS.index(sec) + 1, a)
    )

# =====================================================
# BUILD LIBRARY GRAPH
# =====================================================

graph, coords, meta = build_graph(
    closed,
    restricted,
    crowded
)

# =====================================================
# STARTING LOCATION
# =====================================================

st.sidebar.subheader("Starting Location")

start_floor = st.sidebar.selectbox(
    "Starting floor",
    range(1, 6),
    index=1
)

start_section = st.sidebar.selectbox(
    "Starting section",
    SECTIONS,
    index=0
)

start_aisle = st.sidebar.selectbox(
    "Starting aisle",
    range(1, 4),
    index=0
)

start_shelf = st.sidebar.selectbox(
    "Starting shelf",
    range(1, 5),
    index=0
)

start = node_id(
    start_floor,
    SECTIONS.index(start_section) + 1,
    start_aisle,
    start_shelf
)

# =====================================================
# LOCATION DETAILS
# =====================================================

def locate_text(row):

    return (
        f"Floor {int(row.floor)} → "
        f"{row.section} → "
        f"Aisle {int(row.aisle)} → "
        f"Shelf {int(row.shelf)} → "
        f"Row {int(row.row)} → "
        f"Column {int(row.column)}"
    )

# =====================================================
# DISPLAY BOOK DETAILS
# =====================================================

def show_book(row):

    st.markdown(f"### 📖 {row.title}")

    st.write(
        f"**Author:** {row.author or 'Not listed'}"
    )

    st.write(
        f"**ISBN:** {row.isbn or 'Not listed'}"
    )

    st.success(
        "📍 Book Location: " + locate_text(row)
    )

    if row.availability.startswith("Unavailable"):

        st.error(
            "This book copy is currently unavailable."
        )

    else:

        st.info(
            "Availability: " + row.availability
        )

# =====================================================
# BOOK SEARCH
# =====================================================

def book_search(query, limit=100):

    q = query.strip().lower()

    if not q:
        return df.iloc[0:0]

    mask = (
        df.title.str.lower().str.contains(
            q,
            regex=False
        )
        |
        df.author.str.lower().str.contains(
            q,
            regex=False
        )
        |
        df.isbn.str.lower().str.contains(
            q,
            regex=False
        )
    )

    return df[mask].head(limit)

# =====================================================
# APPLICATION TABS
# =====================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📖 Book Catalogue",
    "🔎 Single Book Finder",
    "🧭 Multiple Book Finder",
    "🏢 Library Map & Details"
])

# =====================================================
# TAB 1: BOOK CATALOGUE
# =====================================================

with tab1:

    st.subheader("Complete Book Catalogue")

    st.write(
        f"**{len(df):,} book records loaded**"
    )

    q = st.text_input(
        "Search by title, author or ISBN",
        key="catalogue_q"
    )

    c1, c2 = st.columns(2)

    with c1:

        floor_filter = st.selectbox(
            "Filter by floor",
            ["All floors", 1, 2, 3, 4, 5],
            key="cat_floor"
        )

    with c2:

        section_filter = st.selectbox(
            "Filter by section",
            ["All sections"] + SECTIONS,
            key="cat_section"
        )

    if q:

        view = book_search(q, 10000)

    else:

        view = df.head(1000)

    if floor_filter != "All floors":

        view = view[
            view.floor == int(floor_filter)
        ]

    if section_filter != "All sections":

        view = view[
            view.section == section_filter
        ]

    cols = [
        "isbn",
        "title",
        "author",
        "year",
        "publisher",
        "floor",
        "section",
        "aisle",
        "shelf",
        "row",
        "column",
        "availability"
    ]

    # Light styled catalogue table
    styled_table = (
        view[cols]
        .head(1000)
        .style
        .set_properties(**{
            "background-color": "#FFFFFF",
            "color": "#243B53",
            "border-color": "#D9E2EC"
        })
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("background-color", "#EAF2F8"),
                    ("color", "#243B53"),
                    ("font-weight", "bold"),
                    ("border-color", "#D9E2EC")
                ]
            },
            {
                "selector": "td",
                "props": [
                    ("background-color", "#FFFFFF"),
                    ("color", "#243B53"),
                    ("border-color", "#D9E2EC")
                ]
            }
        ])
    )

    st.dataframe(
        styled_table,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "⬇ Download Catalogue",
        view[cols].to_csv(index=False).encode("utf-8"),
        "library_catalogue_view.csv",
        "text/csv"
    )

# =====================================================
# TAB 2: SINGLE BOOK FINDER
# =====================================================

with tab2:

    st.subheader("Find a Single Book")

    query = st.text_input(
        "Enter book title, author or ISBN",
        key="single_query"
    )

    matches = book_search(query, 80)

    if query:

        if matches.empty:

            st.warning("No matching book found.")

        else:

            labels = [
                f"{r.title} — {r.author} | ISBN {r.isbn} | record {r.record_id}"
                for r in matches.itertuples()
            ]

            choice = st.selectbox(
                "Select the exact book",
                labels
            )

            selected = matches.iloc[
                labels.index(choice)
            ]

            show_book(selected)

            algorithm = st.radio(
                "Choose Search Algorithm",
                ["BFS", "DFS", "A*"],
                horizontal=True,
                key="single_algo"
            )

            goal = selected.node

            if st.button(
                "🔍 Find Route to Book",
                type="primary"
            ):

                if selected.availability.startswith("Unavailable"):

                    st.error(
                        "This book is unavailable. Choose another result."
                    )

                    st.stop()

                path, opened, closed_nodes, cost = search(
                    graph,
                    start,
                    goal,
                    algorithm,
                    coords
                )

                if not path:

                    st.error(
                        "No route is available. "
                        "A section or shelf may be closed or restricted."
                    )

                else:

                    st.success(
                        f"Route found using {algorithm} | "
                        f"Total path cost: {cost:.1f}"
                    )

                    st.markdown("### 🧭 Route")

                    st.write(
                        " → ".join(path)
                    )

                    st.markdown("### Turn-by-turn directions")

                    for i, (u, v, action) in enumerate(
                        zip(
                            path,
                            path[1:],
                            path_actions(graph, path)
                        ),
                        1
                    ):

                        m = meta[v]

                        st.write(
                            f"**Step {i}:** {action}: "
                            f"Go to Floor {m['floor']}, "
                            f"{m['section']}, "
                            f"Aisle {m['aisle']}, "
                            f"Shelf {m['shelf']}."
                        )

                    if len(path) == 1:

                        st.info(
                            "You are already at the assigned shelf."
                        )

                    with st.expander(
                        "Algorithm Trace: Open List and Closed List"
                    ):

                        st.write(
                            "**Open List:**",
                            opened
                        )

                        st.write(
                            "**Closed List:**",
                            closed_nodes
                        )

                    st.metric(
                        "Nodes Expanded",
                        len(closed_nodes)
                    )

# =====================================================
# TAB 3: MULTIPLE BOOK FINDER
# =====================================================

with tab3:

    st.subheader("Collect Multiple Books")

    q = st.text_input(
        "Search for books to add to your collection",
        key="multi_query"
    )

    matches = book_search(q, 100)

    if q and not matches.empty:

        opts = [
            f"{r.title} — {r.author} | {r.isbn} | record {r.record_id}"
            for r in matches.itertuples()
        ]

        selected_labels = st.multiselect(
            "Select books to collect",
            opts,
            key="multi_select"
        )

        if selected_labels:

            selected_rows = matches.iloc[
                [opts.index(x) for x in selected_labels]
            ]

            st.write(
                f"**{len(selected_rows)} books selected**"
            )

            for r in selected_rows.itertuples():

                st.write(
                    "📖",
                    r.title,
                    "—",
                    locate_text(r)
                )

            algo = st.radio(
                "Choose Route Algorithm",
                ["BFS", "DFS", "A*"],
                horizontal=True,
                key="multi_algo"
            )

            time_limit = st.number_input(
                "Your time limit (walking-cost units)",
                min_value=1,
                value=60
            )

            if st.button(
                "🧭 Plan Collection Route",
                type="primary"
            ):

                unavailable = selected_rows[
                    selected_rows.availability.str.startswith(
                        "Unavailable"
                    )
                ]

                if not unavailable.empty:

                    st.error(
                        "Some selected books are unavailable: "
                        + ", ".join(
                            unavailable.title.tolist()
                        )
                    )

                    st.stop()

                targets = selected_rows.node.tolist()

                route, legs, total, opened, closed_nodes = plan_multiple(
                    graph,
                    start,
                    targets,
                    algo,
                    coords
                )

                if math.isinf(total):

                    st.error(
                        "Could not reach every selected book. "
                        "Check closed or restricted sections."
                    )

                elif total > time_limit:

                    st.warning(
                        f"Route cost {total:.1f} exceeds your "
                        f"time limit of {time_limit}. "
                        "Remove a book or change restrictions."
                    )

                else:

                    st.success(
                        f"Collection route planned | "
                        f"{len(targets)} books | "
                        f"Total cost: {total:.1f}"
                    )

                    st.markdown("### 📚 Collection Stops")

                    for i, (target, path, cost) in enumerate(
                        legs,
                        1
                    ):

                        book = selected_rows[
                            selected_rows.node == target
                        ].iloc[0]

                        st.markdown(
                            f"**Stop {i}: {book.title}**"
                        )

                        st.write(
                            "📍 " + locate_text(book)
                        )

                        st.write(
                            f"Leg cost: {cost:.1f}"
                        )

                        st.write(
                            "Route: " + " → ".join(path)
                        )

                        st.divider()

                    st.markdown("### Complete Collection Route")

                    st.write(
                        " → ".join(route)
                    )

                    with st.expander(
                        "Algorithm Trace: Open List and Closed List"
                    ):

                        st.write(
                            "**Open List:**",
                            opened
                        )

                        st.write(
                            "**Closed List:**",
                            closed_nodes
                        )

    elif q:

        st.warning(
            "No matching books found. Try a shorter title or author name."
        )

# =====================================================
# TAB 4: LIBRARY MAP AND DETAILS
# =====================================================

with tab4:

    st.subheader("Five-Floor Library")

    for f in range(1, 6):

        with st.expander(
            f"🏢 Floor {f}",
            expanded=(f == start_floor)
        ):

            for i, sec in enumerate(SECTIONS, 1):

                st.markdown(
                    f"**{sec}**"
                )

                st.write(
                    "3 aisles · 4 shelves per aisle"
                )

                st.write(
                    "Nodes: "
                    + ", ".join(
                        node_id(f, i, a, h)
                        for a in range(1, 4)
                        for h in range(1, 5)
                    )
                )

    st.subheader("Library Navigation Rules")

    st.write(
        "- Crowded aisle: adds 4 cost units."
    )

    st.write(
        "- Stairs between floors: costs 3 units."
    )

    st.write(
        "- Closed section: its shelf nodes are removed from the graph."
    )

    st.write(
        "- Restricted shelf: that node cannot be traversed."
    )

    st.write(
        "- Unavailable book: cannot be collected."
    )