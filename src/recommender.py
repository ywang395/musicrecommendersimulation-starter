from dataclasses import dataclass
from typing import Dict, List, Tuple


def _normalize_text(value: str) -> str:
    return str(value).strip().lower()


def _clamp_similarity(value: float) -> float:
    return max(0.0, min(1.0, value))


GENRE_SIMILARITY = {
    ("pop", "indie pop"): 0.8,
    ("indie pop", "pop"): 0.8,
    ("rock", "metal"): 0.7,
    ("metal", "rock"): 0.7,
    ("lofi", "ambient"): 0.7,
    ("ambient", "lofi"): 0.7,
    ("jazz", "blues"): 0.6,
    ("blues", "jazz"): 0.6,
    ("r&b", "hip-hop"): 0.6,
    ("hip-hop", "r&b"): 0.6,
}


def genre_similarity(user_genre: str, song_genre: str) -> float:
    user_genre = _normalize_text(user_genre)
    song_genre = _normalize_text(song_genre)

    if user_genre == song_genre:
        return 1.0

    return GENRE_SIMILARITY.get((user_genre, song_genre), 0.0)


MOOD_SIMILARITY = {
    ("happy", "joyful"): 0.8,
    ("joyful", "happy"): 0.8,
    ("sad", "melancholic"): 0.8,
    ("melancholic", "sad"): 0.8,
    ("chill", "relaxed"): 0.7,
    ("relaxed", "chill"): 0.7,
    ("chill", "peaceful"): 0.7,
    ("peaceful", "chill"): 0.7,
    ("focused", "motivated"): 0.6,
    ("motivated", "focused"): 0.6,
    ("dreamy", "romantic"): 0.6,
    ("romantic", "dreamy"): 0.6,
    ("intense", "energetic"): 0.7,
    ("energetic", "intense"): 0.7,
}


def mood_similarity(user_mood: str, song_mood: str) -> float:
    user_mood = _normalize_text(user_mood)
    song_mood = _normalize_text(song_mood)

    if user_mood == song_mood:
        return 1.0

    return MOOD_SIMILARITY.get((user_mood, song_mood), 0.0)


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
    favorite_artist: str = ""
    target_danceability: float = 0.5
    target_valence: float = 0.5


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
            "genre": user.favorite_genre,
            "artist": user.favorite_artist,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
            "danceability": user.target_danceability,
            "valence": user.target_valence,
        }
        scored = []
        for song in self.songs:
            song_dict = {
                "genre": song.genre,
                "mood": song.mood,
                "artist": song.artist,
                "energy": song.energy,
                "danceability": song.danceability,
                "valence": song.valence,
                "acousticness": song.acousticness,
            }
            score, _ = score_song(user_prefs, song_dict)
            scored.append((song, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Summarize why a song matches the user's preferences."""
        user_prefs = {
            "genre": user.favorite_genre,
            "artist": user.favorite_artist,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
            "danceability": user.target_danceability,
            "valence": user.target_valence,
        }
        song_dict = {
            "genre": song.genre,
            "mood": song.mood,
            "artist": song.artist,
            "energy": song.energy,
            "danceability": song.danceability,
            "valence": song.valence,
            "acousticness": song.acousticness,
        }
        score, reasons = score_song(user_prefs, song_dict)
        return f"Score {score:.2f}: " + ", ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            songs.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": _normalize_text(row["genre"]),
                    "mood": _normalize_text(row["mood"]),
                    "energy": float(row["energy"]),
                    "tempo_bpm": float(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                }
            )
        print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """

    user_genre = _normalize_text(user_prefs.get("genre", ""))
    user_artist = _normalize_text(user_prefs.get("artist", ""))
    user_mood = _normalize_text(user_prefs.get("mood", ""))
    user_energy = float(user_prefs.get("energy", 0.5))
    user_danceability = float(user_prefs.get("danceability", 0.5))
    user_valence = float(user_prefs.get("valence", 0.5))
    likes_acoustic = user_prefs.get("likes_acoustic", None)

    song_genre = _normalize_text(song.get("genre", ""))
    song_artist = _normalize_text(song.get("artist", ""))
    song_mood = _normalize_text(song.get("mood", ""))
    song_energy = float(song.get("energy", 0.5))
    song_danceability = float(song.get("danceability", 0.5))
    song_valence = float(song.get("valence", 0.5))
    song_acousticness = float(song.get("acousticness", 0.5))

    genre_score = genre_similarity(user_genre, song_genre)
    mood_score = mood_similarity(user_mood, song_mood)
    artist_score = 1.0 if user_artist and song_artist == user_artist else 0.0
    energy_score = _clamp_similarity(1.0 - abs(song_energy - user_energy))
    danceability_score = _clamp_similarity(1.0 - abs(song_danceability - user_danceability))
    valence_score = _clamp_similarity(1.0 - abs(song_valence - user_valence))

    if likes_acoustic is None:
        acoustic_score = 0.5
    else:
        acoustic_score = song_acousticness if likes_acoustic else (1.0 - song_acousticness)

    weights = {
        "genre": 0.25,
        "mood": 0.20,
        "energy": 0.20,
        "danceability": 0.15,
        "valence": 0.10,
        "acousticness": 0.10,
    }
    if user_artist:
        weights["artist"] = 0.10
        for key in ("danceability", "valence"):
            weights[key] -= 0.05

    score = (
        weights["genre"] * genre_score
        + weights["mood"] * mood_score
        + weights["energy"] * energy_score
        + weights["danceability"] * danceability_score
        + weights["valence"] * valence_score
        + weights["acousticness"] * acoustic_score
        + weights.get("artist", 0.0) * artist_score
    )

    reasons = []
    if genre_score == 1.0:
        reasons.append(f"genre match (+{weights['genre'] * genre_score:.2f})")
    elif genre_score > 0.0:
        reasons.append(f"similar genre match (+{weights['genre'] * genre_score:.2f})")
    if mood_score == 1.0:
        reasons.append(f"mood match (+{weights['mood'] * mood_score:.2f})")
    elif mood_score > 0.0:
        reasons.append(f"similar mood match (+{weights['mood'] * mood_score:.2f})")
    if artist_score:
        reasons.append(f"artist match (+{weights['artist'] * artist_score:.2f})")

    reasons.append(f"energy similarity (+{weights['energy'] * energy_score:.2f})")
    reasons.append(
        f"danceability similarity (+{weights['danceability'] * danceability_score:.2f})"
    )
    reasons.append(f"valence similarity (+{weights['valence'] * valence_score:.2f})")

    if likes_acoustic is not None:
        acoustic_label = "acousticness fit" if likes_acoustic else "low acousticness fit"
        reasons.append(f"{acoustic_label} (+{weights['acousticness'] * acoustic_score:.2f})")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """

    scored = [(song, *score_song(user_prefs, song)) for song in songs]
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)
    return [(song, score, ", ".join(reasons)) for song, score, reasons in ranked[:k]]
