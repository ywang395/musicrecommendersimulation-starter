from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Initialize the recommender with a song catalog."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs ranked for the given user profile."""
        user_prefs = {
            "genre":        user.favorite_genre,
            "mood":         user.favorite_mood,
            "energy":       user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        scored = []
        for song in self.songs:
            song_dict = {
                "genre":        song.genre,
                "mood":         song.mood,
                "energy":       song.energy,
                "acousticness": song.acousticness,
            }
            score, _ = score_song(user_prefs, song_dict)
            scored.append((song, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Summarize why a song matches the user's preferences."""
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"].strip().lower(),
                "mood":         row["mood"].strip().lower(),
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
        print (f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    user_genre     = user_prefs.get("genre", "").lower()
    user_mood      = user_prefs.get("mood", "").lower()
    user_energy    = float(user_prefs.get("energy", 0.5))
    likes_acoustic = user_prefs.get("likes_acoustic", None)

    genre_score  = 1.0 if song["genre"] == user_genre else 0.0
    mood_score   = 1.0 if song["mood"]  == user_mood  else 0.0
    energy_score = 1.0 - abs(song["energy"] - user_energy)

    reasons = []

    # Genre component
    genre_points = 0.35 * genre_score
    if genre_score:
        reasons.append(f"genre match (+{genre_points:.2f})")
    else:
        reasons.append(f"genre mismatch (+0.00)")

    # Mood component
    mood_points = 0.30 * mood_score
    if mood_score:
        reasons.append(f"mood match (+{mood_points:.2f})")
    else:
        reasons.append(f"mood mismatch (+0.00)")

    # Energy component
    delta = abs(song["energy"] - user_energy)
    energy_points = 0.25 * energy_score
    if delta <= 0.20:
        reasons.append(f"energy close to target (+{energy_points:.2f})")
    else:
        reasons.append(f"energy far from target (+{energy_points:.2f})")

    if likes_acoustic is None:
        score = 0.40 * genre_score + 0.35 * mood_score + 0.25 * energy_score
    else:
        acoustic_score = song["acousticness"] if likes_acoustic else (1.0 - song["acousticness"])
        acoustic_points = 0.10 * acoustic_score
        if not likes_acoustic and song["acousticness"] < 0.40:
            reasons.append(f"low acousticness fits preference (+{acoustic_points:.2f})")
        elif likes_acoustic and song["acousticness"] >= 0.60:
            reasons.append(f"high acousticness fits preference (+{acoustic_points:.2f})")
        else:
            reasons.append(f"acousticness partial fit (+{acoustic_points:.2f})")
        score = (0.35 * genre_score + 0.30 * mood_score +
                 0.25 * energy_score + 0.10 * acoustic_score)

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = [(song, *score_song(user_prefs, song)) for song in songs]
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)
    return [(song, score, ", ".join(reasons)) for song, score, reasons in ranked[:k]]
