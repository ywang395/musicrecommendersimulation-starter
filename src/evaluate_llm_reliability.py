from __future__ import annotations

import json

from src.llm_reeval import (
    _MAX_DELTA,
    _NUMERIC_FIELDS,
    call_llm_reeval,
    deterministic_update,
    load_last_n_history,
    load_profile,
)
from src.models import StableUserProfile


def _default_profile() -> StableUserProfile:
    return StableUserProfile(
        favorite_genre="pop",
        favorite_mood="sad",
        target_energy=0.1,
        likes_acoustic=True,
        target_danceability=0.1,
        target_valence=0.1,
        desired_popularity=0.85,
        preferred_decade=2010,
    )


def _reliability_checks(before: StableUserProfile, after: StableUserProfile) -> dict:
    checks = {
        "protected_artist_preserved": before.favorite_artist == after.favorite_artist,
        "protected_mode_preserved": before.scoring_mode == after.scoring_mode,
        "genre_present": bool(after.favorite_genre),
        "mood_present": bool(after.favorite_mood),
    }

    for field in _NUMERIC_FIELDS:
        before_val = float(getattr(before, field))
        after_val = float(getattr(after, field))
        checks[f"{field}_bounded"] = 0.0 <= after_val <= 1.0
        checks[f"{field}_max_delta"] = abs(after_val - before_val) <= (_MAX_DELTA + 1e-9)

    checks["target_tempo_bpm_bounded"] = 40 <= int(after.target_tempo_bpm) <= 220
    checks["target_tempo_bpm_max_delta"] = abs(int(after.target_tempo_bpm) - int(before.target_tempo_bpm)) <= 30

    return checks


def main() -> None:
    history = load_last_n_history("data/history.jsonl")
    stable = load_profile("data/user_profile.json") or _default_profile()
    changes, allow_genre, allow_mood = deterministic_update(history, stable)

    print("=== LLM Reliability Evaluation ===")
    print(f"history_events={len(history)}")
    print(f"candidate_changes={json.dumps(changes, sort_keys=True)}")
    print(f"allow_genre_change={allow_genre}")
    print(f"allow_mood_change={allow_mood}")

    if not changes:
        print("No deterministic candidate changes found; nothing to evaluate.")
        return

    candidate, method = call_llm_reeval(history, stable, changes, allow_genre, allow_mood)
    checks = _reliability_checks(stable, candidate)

    print(f"llm_method={method}")
    print(f"candidate_profile={json.dumps(candidate.to_dict(), sort_keys=True)}")
    print("checks=")
    for name, passed in checks.items():
        print(f"  {name}={passed}")

    if all(checks.values()):
        print("result=PASS")
    else:
        print("result=FAIL")


if __name__ == "__main__":
    main()
