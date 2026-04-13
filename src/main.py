"""
Command line runner for the Music Recommender Simulation.
"""

import os
import sys
import textwrap

sys.path.insert(0, os.path.dirname(__file__))
from recommender import SCORING_MODES, load_songs, recommend_songs


def _truncate(text: str, width: int) -> str:
    if len(text) <= width:
        return text
    if width <= 3:
        return text[:width]
    return text[: width - 3] + "..."


def _print_table(rows, headers) -> None:
    widths = []
    for index, header in enumerate(headers):
        cell_width = 0
        for row in rows:
            lines = str(row[index]).splitlines() or [""]
            cell_width = max(cell_width, max(len(line) for line in lines))
        widths.append(max(len(header), cell_width))

    border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
    header_row = "| " + " | ".join(header.ljust(widths[i]) for i, header in enumerate(headers)) + " |"

    print(border)
    print(header_row)
    print(border)
    for row in rows:
        split_cells = [str(cell).splitlines() or [""] for cell in row]
        row_height = max(len(cell_lines) for cell_lines in split_cells)
        for line_index in range(row_height):
            rendered = []
            for col_index, cell_lines in enumerate(split_cells):
                line = cell_lines[line_index] if line_index < len(cell_lines) else ""
                rendered.append(line.ljust(widths[col_index]))
            print("| " + " | ".join(rendered) + " |")
        print(border)


def _wrap_reasons(text: str, width: int = 56) -> str:
    parts = [part.strip() for part in text.split(",")]
    wrapped_lines = []
    for part in parts:
        wrapped_lines.extend(textwrap.wrap(part, width=width) or [""])
    return "\n".join(wrapped_lines)


def _format_reasons(text: str, width: int = 56, points_width: int = 8) -> str:
    parts = [part.strip() for part in text.split(",")]
    lines = []
    for part in parts:
        marker = " ("
        if marker in part and part.endswith(")"):
            label, points = part.rsplit(marker, 1)
            points = "(" + points
            label_width = max(8, width - points_width - 1)
            wrapped_label_lines = textwrap.wrap(label.strip(), width=label_width) or [""]
            for index, label_line in enumerate(wrapped_label_lines):
                if index == len(wrapped_label_lines) - 1:
                    lines.append(f"{label_line.ljust(label_width)} {points.rjust(points_width)}")
                else:
                    lines.append(label_line)
        else:
            lines.extend(textwrap.wrap(part, width=width) or [""])
    return "\n".join(lines)


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Switch this value to "genre_first", "mood_first", or "energy_focused".
    mode = "mood_first"
    user_prefs = {
        "genre": "pop",
        "mood": "sad",
        "energy": 0.1,
        "danceability": 0.1,
        "valence": 0.1,
        "likes_acoustic": True,
        "popularity": 0.85,
        "release_decade": 2010,
        "mood_tags": [],
        "live_energy": 0.2,
        "lyrical_depth": 0.35,
        "instrumentalness": 0.0,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5, mode=mode)

    print("\n" + "=" * 88)
    print("TOP RECOMMENDATIONS")
    print(f"mode={mode} | available_modes={', '.join(SCORING_MODES.keys())}")
    print(
        "genre={genre} | mood={mood} | energy={energy} | decade={decade} | tags={tags}".format(
            genre=user_prefs["genre"],
            mood=user_prefs["mood"],
            energy=user_prefs["energy"],
            decade=user_prefs["release_decade"],
            tags="|".join(user_prefs["mood_tags"]),
        )
    )
    print("=" * 88)

    rows = []
    for index, (song, score, explanation) in enumerate(recommendations, start=1):
        rows.append(
            [
                index,
                _truncate(song["title"], 18),
                _truncate(song["artist"], 14),
                song["genre"],
                song["mood"],
                f"{score:.2f}",
                _format_reasons(explanation),
            ]
        )

    _print_table(rows, ["#", "Title", "Artist", "Genre", "Mood", "Score", "Reasons"])


if __name__ == "__main__":
    main()
