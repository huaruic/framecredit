"""Pure Source Signature scheduling logic for the throwaway prototype."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import ceil


@dataclass(frozen=True)
class MarkerWindow:
    start: float
    end: float
    position: str


@dataclass(frozen=True)
class CardWindow:
    start: float
    end: float


@dataclass(frozen=True)
class SourceSignaturePlan:
    duration: float
    marker_windows: tuple[MarkerWindow, ...]
    card_windows: tuple[CardWindow, ...]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def build_plan(
    duration: float,
    marker_interval: float = 4.0,
    card_duration: float = 1.5,
) -> SourceSignaturePlan:
    """Return a deterministic attribution schedule without performing I/O."""
    if duration <= 0:
        raise ValueError("duration must be positive")
    if marker_interval <= 0:
        raise ValueError("marker_interval must be positive")
    if card_duration <= 0 or card_duration > duration:
        raise ValueError("card_duration must be positive and no longer than duration")

    positions = ("top_left", "top_right", "center")
    marker_windows = tuple(
        MarkerWindow(
            start=index * marker_interval,
            end=min((index + 1) * marker_interval, duration),
            position=positions[index % len(positions)],
        )
        for index in range(ceil(duration / marker_interval))
    )

    starts = (
        0.0,
        max(0.0, (duration - card_duration) / 2),
        max(0.0, duration - card_duration),
    )
    card_windows = tuple(
        CardWindow(start=start, end=min(start + card_duration, duration))
        for start in starts
    )

    return SourceSignaturePlan(
        duration=duration,
        marker_windows=marker_windows,
        card_windows=card_windows,
    )
