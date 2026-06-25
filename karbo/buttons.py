"""
Inline-button builders for the Karbo Bot API.

The HTTP wire format is just JSON dicts, but typing them as plain
`dict`s in user code is painful. This module provides small, frozen
dataclasses + a `to_dict()` serializer so a bot can write::

    from karbo import KarboBot, Button, ButtonStyle, Pulse, SparkParticles

    await bot.send_message(
        chat_id,
        "Confirm payment?",
        buttons=[[
            Button(
                id="pay",
                label="Pay",
                style=ButtonStyle(
                    color="#22C55E",
                    text_color="#FFFFFF",
                    shape="capsule",
                ),
                animations=[Pulse(speed_ms=900)],
                particles=SparkParticles(color="#FFD54F"),
            ),
            Button(
                id="cancel",
                label="Cancel",
                style=ButtonStyle(color="#1F2937", text_color="#FFFFFF"),
            ),
        ]],
    )

Anything you pass goes through `validate_inline_buttons` server-side, so
client validation is intentionally light — we just shape the JSON.

You can also bypass these classes entirely and pass raw `List[List[dict]]`
to `send_message(buttons=...)` if you prefer.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, List, Optional, Sequence, Union


__all__ = [
    "Button",
    "ButtonStyle",
    "Gradient",
    "TapInteraction",
    "SwipeInteraction",
    "Pulse",
    "Neon",
    "Glitch",
    "Outline",
    "Particles",
    "SparkParticles",
    "ConfettiParticles",
    "HeartParticles",
    "PixelParticles",
    "SmokeParticles",
    "buttons_to_dict",
    "ButtonPress",
]


# ── Style / decoration ──────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class Gradient:
    start: str
    end: str
    # 'horizontal' | 'vertical' | 'diagonal' | 'radial'
    direction: str = "horizontal"

    def _to_dict(self) -> dict:
        return {
            "start_hex": self.start,
            "end_hex": self.end,
            "direction": self.direction,
        }


@dataclass(frozen=True, slots=True)
class ButtonStyle:
    """Visual style: bg color, text color, optional gradient, shape."""

    color: str = "#6C8CFF"
    text_color: str = "#FFFFFF"
    gradient: Optional[Gradient] = None
    # 'rectangle' | 'circle' | 'capsule'
    shape: str = "rectangle"
    corner_radius: int = 12

    def _to_dict(self) -> dict:
        return {
            "shape": self.shape,
            "corner_radius": self.corner_radius,
            "color": {
                "hex": self.color,
                "text_hex": self.text_color,
                "gradient": self.gradient._to_dict() if self.gradient else None,
            },
        }


# ── Interactions ────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class TapInteraction:
    """Default — single tap fires the press event."""

    def _to_dict(self) -> dict:
        return {"type": "tap"}


@dataclass(frozen=True, slots=True)
class SwipeInteraction:
    """Drag-to-confirm. ``text`` is shown while the user swipes."""

    text: str
    fill_color: str = "#22C55E"

    def _to_dict(self) -> dict:
        return {
            "type": "swipe",
            "swipe": {"text": self.text, "fill_hex": self.fill_color},
        }


Interaction = Union[TapInteraction, SwipeInteraction]


# ── Animations ──────────────────────────────────────────────────────


class _Animation:
    """Internal base."""

    def _to_dict(self) -> dict:  # pragma: no cover
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class Pulse(_Animation):
    speed_ms: int = 1200

    def _to_dict(self) -> dict:
        return {"kind": "pulse", "speed_ms": self.speed_ms}


@dataclass(frozen=True, slots=True)
class Neon(_Animation):
    color: str = "#6C8CFF"
    blur: int = 12

    def _to_dict(self) -> dict:
        return {"kind": "neon", "color_hex": self.color, "blur": self.blur}


@dataclass(frozen=True, slots=True)
class Glitch(_Animation):
    intensity_px: int = 3
    frequency_ms: int = 2500

    def _to_dict(self) -> dict:
        return {
            "kind": "glitch",
            "intensity_px": self.intensity_px,
            "frequency_ms": self.frequency_ms,
        }


@dataclass(frozen=True, slots=True)
class Outline(_Animation):
    color: str = "#FFFFFF"
    thickness_px: int = 2
    corner_radius: int = 12

    def _to_dict(self) -> dict:
        return {
            "kind": "outline",
            "color_hex": self.color,
            "thickness_px": self.thickness_px,
            "corner_radius": self.corner_radius,
        }


# ── Particles ───────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class Particles:
    """Generic particles config — usually use one of the typed subclasses
    (``SparkParticles``, ``ConfettiParticles``, ...) for readability.
    """

    type: str
    color: str = "#FFD54F"
    intensity: int = 3  # 1..5

    def _to_dict(self) -> dict:
        return {
            "type": self.type,
            "color_hex": self.color,
            "intensity": self.intensity,
        }


def SparkParticles(color: str = "#FFD54F", intensity: int = 3) -> Particles:
    return Particles(type="spark", color=color, intensity=intensity)


def ConfettiParticles(
    color: str = "#FF7AB6", intensity: int = 3,
) -> Particles:
    return Particles(type="confetti", color=color, intensity=intensity)


def HeartParticles(color: str = "#FF4D6D", intensity: int = 3) -> Particles:
    return Particles(type="heart", color=color, intensity=intensity)


def PixelParticles(color: str = "#22C55E", intensity: int = 3) -> Particles:
    return Particles(type="pixel", color=color, intensity=intensity)


def SmokeParticles(color: str = "#9CA3AF", intensity: int = 3) -> Particles:
    return Particles(type="smoke", color=color, intensity=intensity)


# ── Button itself ───────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class Button:
    """One inline button.

    Required: ``id`` (stable identifier passed back on press) and
    ``label`` (text shown on the button). Everything else is optional.
    """

    id: str
    label: str
    style: ButtonStyle = field(default_factory=ButtonStyle)
    interaction: Interaction = field(default_factory=TapInteraction)
    animations: Sequence[_Animation] = ()
    particles: Optional[Particles] = None

    def _to_dict(self) -> dict:
        style = self.style._to_dict()
        out = {
            "id": self.id,
            "label": self.label,
            **style,
            "interaction": self.interaction._to_dict(),
            "animations": [a._to_dict() for a in self.animations],
            "particles": self.particles._to_dict() if self.particles else None,
        }
        return out


# ── Top-level helpers ───────────────────────────────────────────────


# A row of buttons can be expressed three ways:
#   * `Button` objects in a list (typed, recommended)
#   * raw `dict`s in a list (escape hatch for advanced/new fields)
#   * a single `Button` (will be wrapped into a 1-button row)
RowItem = Union[Button, dict]
Row = Union[Button, Sequence[RowItem]]


def buttons_to_dict(rows: Sequence[Row]) -> List[List[dict]]:
    """Serialize a list of rows into the wire format the server expects.

    Accepts either typed `Button`s or raw dicts in any combination —
    bots that want to use brand-new server features can pass raw dicts
    while keeping the rest of the API typed.
    """
    out: List[List[dict]] = []
    for row in rows:
        if isinstance(row, Button):
            out.append([row._to_dict()])
            continue
        out_row: List[dict] = []
        for item in row:
            if isinstance(item, Button):
                out_row.append(item._to_dict())
            elif isinstance(item, dict):
                out_row.append(item)
            else:
                raise TypeError(
                    f"Inline button must be karbo.Button or dict, "
                    f"got {type(item).__name__}"
                )
        if out_row:
            out.append(out_row)
    return out


# ── Server → client event payload ──────────────────────────────────


@dataclass(frozen=True, slots=True)
class ButtonPress:
    """Delivered to the bot's WS handler when a user presses a button.

    `interaction` is one of ``'tap'`` or ``'swipe'`` — same as the
    server's echoed type. A single handler can branch on it instead
    of registering separate callbacks per interaction.
    """

    chat_id: str
    message_id: str
    button_id: str
    user_id: str
    community_id: int
    interaction: str
