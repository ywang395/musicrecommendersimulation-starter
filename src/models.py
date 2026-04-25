from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import List


@dataclass
class StableUserProfile:
    # Required categorical fields
    favorite_genre: str
    favorite_mood: str

    # Protected categoricals — never overwritten by LLM
    favorite_artist: str = ""
    scoring_mode: str = "balanced"  # balanced|genre_first|mood_first|energy_focused

    # Numeric targets — LLM-adjustable, clamped [0,1], max delta ±0.3/session
    target_energy: float = 0.5
    target_danceability: float = 0.5
    target_valence: float = 0.5
    target_live_energy: float = 0.5
    target_lyrical_depth: float = 0.5
    target_instrumentalness: float = 0.5
    target_tempo_bpm: int = 100
    desired_popularity: float = 0.5
    preferred_decade: int = 2010

    # Bool — LLM-adjustable
    likes_acoustic: bool = False

    # Tag list — LLM-adjustable
    preferred_mood_tags: List[str] = field(default_factory=list)

    # Versioning — managed by profile updater, never set by LLM
    version: int = 1
    last_updated: str = ""
    update_reason: str = ""
    previous_version: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class SessionState:
    session_id: str
    stable_profile: StableUserProfile

    # Short-term interaction counters
    recent_skips: List[int] = field(default_factory=list)
    recent_repeats: List[int] = field(default_factory=list)
    recent_completes: List[int] = field(default_factory=list)

    # Ephemeral numeric nudges applied on top of StableUserProfile targets
    energy_nudge: float = 0.0
    danceability_nudge: float = 0.0
    valence_nudge: float = 0.0

    # Queue context
    played_ids: List[int] = field(default_factory=list)
    current_queue: List[dict] = field(default_factory=list)

    # Recompute state
    skips_since_last_recompute: int = 0
    recompute_count: int = 0


@dataclass(frozen=True)
class InteractionEvent:
    # "complete" | "skip" | "repeat" | "quit"
    # quit = session termination, NOT a dislike signal
    event_type: str
    session_id: str
    song_id: int
    song_title: str
    song_artist: str
    song_genre: str
    song_mood: str
    song_energy: float
    song_valence: float
    song_tempo_bpm: float
    song_score: float
    elapsed_seconds: float
    total_duration: float
    elapsed_ratio: float    # elapsed / total_duration; 0.0 for repeat events
    repeat_count: int       # 0 unless event_type == "repeat"
    timestamp: str          # ISO 8601 UTC

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)
