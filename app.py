import random
import time

import numpy as np
import streamlit as st
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates

N = 50
BOARD_SIZE = 800
CELL_SIZE = BOARD_SIZE // N

st.set_page_config(
    page_title="Conway's Game of Life",
    page_icon="🧬",
    layout="wide",
)

st.markdown(
    """
    <style>
      .main .block-container {
        max-width: 1250px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
      }
      h1 { color: #60d394; }
      div[data-testid="stMetric"] {
        background: #172536;
        border: 1px solid #34465d;
        padding: 12px 16px;
        border-radius: 12px;
      }
      .hint { color: #9fb0c4; font-size: .95rem; }
      div[data-testid="stImage"] img {
        display: block;
        margin-left: auto;
        margin-right: auto;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Conway's Game of Life")
st.caption("Interaktivní simulace buněčného automatu")


def empty_grid():
    return np.zeros((N, N), dtype=np.uint8)


def count_neighbors(grid, row, col):
    r0, r1 = max(0, row - 1), min(N, row + 2)
    c0, c1 = max(0, col - 1), min(N, col + 2)
    return int(grid[r0:r1, c0:c1].sum() - grid[row, col])


def next_generation(grid):
    result = np.zeros_like(grid)
    for row in range(N):
        for col in range(N):
            neighbors = count_neighbors(grid, row, col)
            if grid[row, col] == 1:
                result[row, col] = 1 if neighbors in (2, 3) else 0
            else:
                result[row, col] = 1 if neighbors == 3 else 0
    return result


def make_board_image(grid):
    """Vytvoří jednu kompletní interaktivní plochu 50 × 50."""
    image = Image.new("RGB", (BOARD_SIZE, BOARD_SIZE), "#07111e")
    draw = ImageDraw.Draw(image)

    for row in range(N):
        for col in range(N):
            if grid[row, col]:
                x0 = col * CELL_SIZE + 1
                y0 = row * CELL_SIZE + 1
                x1 = (col + 1) * CELL_SIZE - 2
                y1 = (row + 1) * CELL_SIZE - 2
                draw.rectangle((x0, y0, x1, y1), fill="#60d394")

    for i in range(N + 1):
        pos = i * CELL_SIZE
        draw.line((pos, 0, pos, BOARD_SIZE), fill="#26384d", width=1)
        draw.line((0, pos, BOARD_SIZE, pos), fill="#26384d", width=1)

    return image


PATTERNS = {
    "Kluzák (Glider)": [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
    "Blikač (Blinker)": [(0, 0), (0, 1), (0, 2)],
    "Pulzar (Pulsar)": (
        [(0, x) for x in (2, 3, 4, 8, 9, 10)]
        + [(5, x) for x in (2, 3, 4, 8, 9, 10)]
        + [(7, x) for x in (2, 3, 4, 8, 9, 10)]
        + [(12, x) for x in (2, 3, 4, 8, 9, 10)]
        + [(y, 0) for y in (2, 3, 4, 8, 9, 10)]
        + [(y, 5) for y in (2, 3, 4, 8, 9, 10)]
        + [(y, 7) for y in (2, 3, 4, 8, 9, 10)]
        + [(y, 12) for y in (2, 3, 4, 8, 9, 10)]
    ),
}

if "grid" not in st.session_state:
    st.session_state.grid = empty_grid()
if "generation" not in st.session_state:
    st.session_state.generation = 0
if "board_version" not in st.session_state:
    st.session_state.board_version = 0

grid = st.session_state.grid
alive_count = int(grid.sum())

m1, m2, m3 = st.columns(3)
m1.metric("Generace", st.session_state.generation)
m2.metric("Živé buňky", alive_count)
m3.metric("Velikost mřížky", "50 × 50")

st.subheader("Hrací plocha")
st.markdown(
    '<p class="hint">Všech 2 500 buněk je zobrazeno najednou. Kliknutím nebo '
    'klepnutím na buňku ji zapneš či vypneš. Hrací plocha nemá vlastní posuvníky.</p>',
    unsafe_allow_html=True,
)

board_image = make_board_image(st.session_state.grid)
click = streamlit_image_coordinates(
    board_image,
    width=BOARD_SIZE,
    key=f"board_click_{st.session_state.board_version}",
)

if click is not None and "x" in click and "y" in click:
    col = int(click["x"] // CELL_SIZE)
    row = int(click["y"] // CELL_SIZE)
    if 0 <= row < N and 0 <= col < N:
        updated = st.session_state.grid.copy()
        updated[row, col] = 0 if updated[row, col] else 1
        st.session_state.grid = updated
        st.session_state.board_version += 1
        st.rerun()

st.caption("Zelená buňka = živá · Tmavá buňka = mrtvá")

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
        st.session_state.grid = np.array(
            [[1 if random.random() < 0.25 else 0 for _ in range(N)] for _ in range(N)],
            dtype=np.uint8,
        )
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
        "Počet generací", min_value=1, max_value=500, value=50, step=10
    )
with a2:
    delay = st.slider(
        "Prodleva mezi kroky (s)", min_value=0.0, max_value=0.2,
        value=0.02, step=0.01
    )
with a3:
    run_batch = st.button(
        "▶ Spustit simulaci", type="primary", use_container_width=True
    )

if run_batch:
    progress = st.progress(0, text="Simulace probíhá…")
    current = st.session_state.grid.copy()
    total = int(generations)
    for i in range(total):
        current = next_generation(current)
        if delay:
            time.sleep(delay)
        progress.progress(
            (i + 1) / total,
            text=f"Zpracována generace {st.session_state.generation + i + 1} z {total}",
        )
    st.session_state.grid = current
    st.session_state.generation += total
    st.session_state.board_version += 1
    st.rerun()

st.markdown("**Vložit známý vzor**")
p1, p2 = st.columns([2, 1])
with p1:
    selected_pattern = st.selectbox(
        "Vyber vzor", list(PATTERNS.keys()), label_visibility="collapsed"
    )
with p2:
    place_pattern = st.button("Vložit vzor", use_container_width=True)

if place_pattern:
    updated = st.session_state.grid.copy()
    points = PATTERNS[selected_pattern]
    offset = (N - 13) // 2 if selected_pattern == "Pulzar (Pulsar)" else (N - 3) // 2
    for dr, dc in points:
        row, col = offset + dr, offset + dc
        if 0 <= row < N and 0 <= col < N:
            updated[row, col] = 1
    st.session_state.grid = updated
    st.session_state.board_version += 1
    st.rerun()

st.divider()
st.subheader("Pravidla hry")
st.markdown(
    """
    1. **Zrození:** mrtvá buňka ožije, pokud má přesně 3 živé sousedy.
    2. **Přežití:** živá buňka přežije, pokud má 2 nebo 3 živé sousedy.
    3. **Samota:** živá buňka s méně než 2 sousedy zemře.
    4. **Přelidnění:** živá buňka s více než 3 sousedy zemře.

    Každá buňka má maximálně 8 sousedů. Buňky za okrajem mřížky jsou považovány za mrtvé.
    """
)
st.caption("Conway's Game of Life · mřížka 50 × 50 · Python + Streamlit")
