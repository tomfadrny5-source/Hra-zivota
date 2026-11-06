import time
import random
import pandas as pd
import streamlit as st

SIZE = 50
COLUMNS = [f"{i+1:02d}" for i in range(SIZE)]

st.set_page_config(
    page_title="Conway's Game of Life",
    page_icon="🧬",
    layout="wide",
)

st.markdown("""
<style>
    .main .block-container {max-width: 1200px; padding-top: 2rem;}
    div[data-testid="stMetric"] {
        background: #172536;
        border: 1px solid #34465d;
        padding: 12px 16px;
        border-radius: 12px;
    }
    h1 {color: #60d394;}
    .hint {color: #9fb0c4; font-size: .95rem;}
</style>
""", unsafe_allow_html=True)

st.title("Conway's Game of Life")
st.caption("Interaktivní simulace buněčného automatu")

def empty_grid():
    return [[False for _ in range(SIZE)] for _ in range(SIZE)]

def count_neighbors(grid, row, col):
    total = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, col + dc
            if 0 <= r < SIZE and 0 <= c < SIZE:
                total += bool(grid[r][c])
    return total

def next_generation(grid):
    new_grid = empty_grid()
    for r in range(SIZE):
        for c in range(SIZE):
            neighbors = count_neighbors(grid, r, c)
            alive = bool(grid[r][c])
            if alive and neighbors in (2, 3):
                new_grid[r][c] = True
            elif not alive and neighbors == 3:
                new_grid[r][c] = True
    return new_grid

PATTERNS = {
    "Kluzák (Glider)": [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
    "Blikač (Blinker)": [(0, 0), (0, 1), (0, 2)],
    "Pulzar (Pulsar)": (
        [(0, x) for x in (2, 3, 4, 8, 9, 10)] +
        [(5, x) for x in (2, 3, 4, 8, 9, 10)] +
        [(7, x) for x in (2, 3, 4, 8, 9, 10)] +
        [(12, x) for x in (2, 3, 4, 8, 9, 10)] +
        [(y, 0) for y in (2, 3, 4, 8, 9, 10)] +
        [(y, 5) for y in (2, 3, 4, 8, 9, 10)] +
        [(y, 7) for y in (2, 3, 4, 8, 9, 10)] +
        [(y, 12) for y in (2, 3, 4, 8, 9, 10)]
    ),
}

if "grid" not in st.session_state:
    st.session_state.grid = empty_grid()
if "generation" not in st.session_state:
    st.session_state.generation = 0
if "board_version" not in st.session_state:
    st.session_state.board_version = 0

grid = st.session_state.grid
alive_count = sum(sum(row) for row in grid)

m1, m2, m3 = st.columns(3)
m1.metric("Generace", st.session_state.generation)
m2.metric("Živé buňky", alive_count)
m3.metric("Velikost mřížky", "50 × 50")

st.subheader("Hrací plocha")
st.markdown(
    '<p class="hint">Zaškrtnutím políčka vytvoříš živou buňku. '
    'Odškrtnutím ji odstraníš. Na menším displeji lze tabulku posouvat do stran.</p>',
    unsafe_allow_html=True,
)

# Editable 50 x 50 boolean table. The Python code below performs the simulation.
board_key = f"board_editor_{st.session_state.board_version}"
board_df = pd.DataFrame(st.session_state.grid, columns=COLUMNS)
edited_df = st.data_editor(
    board_df,
    key=board_key,
    hide_index=True,
    width="stretch",
    height=520,
    row_height=26,
    disabled=False,
    column_config={
        col: st.column_config.CheckboxColumn(
            label=col,
            help=f"Sloupec {col}",
            width="small",
        )
        for col in COLUMNS
    },
)

# Save manual edits before applying any action.
st.session_state.grid = edited_df.fillna(False).astype(bool).values.tolist()
st.session_state.grid = [
    [bool(cell) for cell in row] for row in st.session_state.grid
]

st.divider()
st.subheader("Ovládání")

c1, c2, c3 = st.columns(3)
with c1:
    if st.button("⏭ Jeden krok", use_container_width=True):
        st.session_state.grid = next_generation(st.session_state.grid)
        st.session_state.generation += 1
        st.session_state.board_version += 1
        st.rerun()
with c2:
    if st.button("🎲 Náhodně", use_container_width=True):
        st.session_state.grid = [
            [random.random() < 0.25 for _ in range(SIZE)]
            for _ in range(SIZE)
        ]
        st.session_state.generation = 0
        st.session_state.board_version += 1
        st.rerun()
with c3:
    if st.button("✖ Vymazat", use_container_width=True):
        st.session_state.grid = empty_grid()
        st.session_state.generation = 0
        st.session_state.board_version += 1
        st.rerun()

st.markdown("**Automatický běh**")
a1, a2, a3 = st.columns([1, 1, 2])
with a1:
    generations = st.number_input(
        "Počet generací",
        min_value=1,
        max_value=500,
        value=50,
        step=10,
    )
with a2:
    delay = st.slider(
        "Prodleva mezi kroky (s)",
        min_value=0.0,
        max_value=0.2,
        value=0.02,
        step=0.01,
    )
with a3:
    run_batch = st.button(
        "▶ Spustit simulaci",
        type="primary",
        use_container_width=True,
    )

if run_batch:
    progress = st.progress(0, text="Simulace probíhá…")
    current = st.session_state.grid
    for i in range(int(generations)):
        current = next_generation(current)
        if delay:
            time.sleep(delay)
        progress.progress(
            (i + 1) / int(generations),
            text=f"Generace {st.session_state.generation + i + 1} zpracována",
        )
    st.session_state.grid = current
    st.session_state.generation += int(generations)
    st.session_state.board_version += 1
    st.rerun()

st.markdown("**Vložit známý vzor**")
pattern_col, button_col = st.columns([2, 1])
with pattern_col:
    selected_pattern = st.selectbox(
        "Vyber vzor",
        list(PATTERNS.keys()),
        label_visibility="collapsed",
    )
with button_col:
    place_pattern = st.button("Vložit vzor", use_container_width=True)

if place_pattern:
    updated = [row[:] for row in st.session_state.grid]
    points = PATTERNS[selected_pattern]
    offset = (SIZE - 13) // 2 if selected_pattern == "Pulzar (Pulsar)" else (SIZE - 3) // 2
    for dr, dc in points:
        r, c = offset + dr, offset + dc
        if 0 <= r < SIZE and 0 <= c < SIZE:
            updated[r][c] = True
    st.session_state.grid = updated
    st.session_state.board_version += 1
    st.rerun()

st.divider()
st.subheader("Pravidla hry")
st.markdown("""
1. **Zrození:** mrtvá buňka ožije, pokud má přesně 3 živé sousedy.
2. **Přežití:** živá buňka přežije, pokud má 2 nebo 3 živé sousedy.
3. **Samota:** živá buňka s méně než 2 sousedy zemře.
4. **Přelidnění:** živá buňka s více než 3 sousedy zemře.

Každá buňka má maximálně 8 sousedů. Okraje mřížky jsou považovány za okraj světa;
buňky za mřížkou jsou mrtvé.
""")
st.caption("Conway's Game of Life · mřížka 50 × 50 · Python + Streamlit")
