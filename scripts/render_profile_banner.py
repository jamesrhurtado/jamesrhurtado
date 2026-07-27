#!/usr/bin/env python3
"""Render James's Windows 95-inspired Clippy profile banner.

The Clippy movements are composited directly from the GIFs supplied through
Yuteoctober/wins95Portfolio. See assets/clippy-source/ATTRIBUTION.md.
The interface, copy, timing, and final GIF assembly are deterministic.
"""

from __future__ import annotations

import argparse
import math
import random
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
CLIPPY_DIR = ROOT / "assets" / "clippy-source"
SPRITE_PATH = ROOT / "assets" / "profile-assistant-sprite.png"
OUTPUT_PATH = ROOT / "assets" / "profile-assistant-banner.gif"
CONTACT_SHEET_PATH = Path(tempfile.gettempdir()) / "profile-assistant-preview.png"

WIDTH, HEIGHT = 960, 420

TEAL = "#087f7f"
TEAL_DARK = "#006666"
NAVY = "#000080"
GRAY = "#c0c0c0"
GRAY_LIGHT = "#ffffff"
GRAY_DARK = "#808080"
BLACK = "#101010"
CREAM = "#fffbd6"
AMBER = "#f0b429"

MESSAGES = [
    "Oh, hello! It looks like you’ve wandered into James’ GitHub profile. "
    "Need a guide?",
    "James is a software engineer who likes building products, automating "
    "things, and negotiating with stubborn bugs.",
    "He’s also a GitHub Campus Expert and Microsoft Student Ambassador from "
    "LATAM. Yes, he likes communities too.",
    "You’ll find him at tech events, usually attending, sometimes speaking, "
    "and always wanting to meet interesting people.",
    "On Instagram, he shares lessons, useful resources, and experiences—"
    "mostly so someone else can avoid the same mistakes.",
    "I found some interesting projects below. Keep scrolling—or check out "
    "his portfolio. I already did the paperwork.",
]

QUOTE_INTRO = "Hey, I’m not done yet! Here’s a quote to brighten your day."

MOTIVATIONS = [
    ("You’re doing great! Keep up the good work.", 3),
    ("Everyone makes mistakes – it’s how we learn and grow.", 1),
    ("Believe in yourself – you’re capable of amazing things.", 2),
    ("Hard work pays off – keep pushing towards your goals!", 3),
    ("Success is not about being the best, but being your best self.", 4),
    ("Stay positive – your attitude can change everything.", 5),
    ("Even on the darkest days, there’s always a glimmer of hope.", 6),
    ("Never give up – your persistence will pay off in the end.", 7),
    ("The only limit is your imagination – let it soar!", 2),
    ("Your words have power – use them wisely and with kindness.", 7),
    ("Trust your instincts – they’re often wiser than you think.", 4),
    ("Embrace the challenges, they’ll make you stronger in the end.", 6),
    ("Sometimes, a simple ‘thank you’ can make a big difference.", 5),
    ("Success is not about the destination, it’s about the journey.", 1),
]

CLIPPY_FONT = CLIPPY_DIR / "MS Sans Serif 8pt bold.ttf"
TITLE_FONT = ImageFont.truetype(str(CLIPPY_FONT), 22)
BODY_FONT = ImageFont.truetype(str(CLIPPY_FONT), 30)
STATUS_FONT = ImageFont.truetype(str(CLIPPY_FONT), 16)
TINY_FONT = ImageFont.truetype(str(CLIPPY_FONT), 14)


def ease_out_back(value: float) -> float:
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (value - 1) ** 3 + c1 * (value - 1) ** 2


def ease_in_out(value: float) -> float:
    return -(math.cos(math.pi * value) - 1) / 2


def beveled_rect(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: str,
    raised: bool = True,
    width: int = 3,
) -> None:
    x1, y1, x2, y2 = box
    draw.rectangle(box, fill=fill)
    top_left = GRAY_LIGHT if raised else GRAY_DARK
    bottom_right = GRAY_DARK if raised else GRAY_LIGHT
    for offset in range(width):
        draw.line(
            (x1 + offset, y2 - offset, x2 - offset, y2 - offset),
            fill=bottom_right,
        )
        draw.line(
            (x2 - offset, y1 + offset, x2 - offset, y2 - offset),
            fill=bottom_right,
        )
        draw.line(
            (x1 + offset, y1 + offset, x2 - offset, y1 + offset),
            fill=top_left,
        )
        draw.line(
            (x1 + offset, y1 + offset, x1 + offset, y2 - offset),
            fill=top_left,
        )


def draw_desktop() -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), TEAL)
    draw = ImageDraw.Draw(image)
    for x in range(-HEIGHT, WIDTH, 32):
        draw.line((x, 0, x + HEIGHT, HEIGHT), fill=TEAL_DARK, width=1)
    draw.rectangle((0, HEIGHT - 10, WIDTH, HEIGHT), fill="#005f5f")
    return image


def draw_window() -> Image.Image:
    window = Image.new("RGBA", (900, 370), (0, 0, 0, 0))
    draw = ImageDraw.Draw(window)
    beveled_rect(draw, (0, 0, 899, 369), GRAY, raised=True, width=4)

    draw.rectangle((8, 8, 891, 53), fill=NAVY)
    draw.rectangle((17, 18, 31, 38), fill=AMBER)
    draw.rectangle((20, 15, 28, 41), outline=GRAY_LIGHT, width=2)
    draw.text((42, 18), "JAMES.EXE — PROFILE ASSISTANT", font=TITLE_FONT, fill="white")

    for index, symbol in enumerate(("_", "□", "×")):
        left = 775 + index * 36
        beveled_rect(draw, (left, 14, left + 30, 45), GRAY, raised=True, width=2)
        bbox = draw.textbbox((0, 0), symbol, font=TITLE_FONT)
        tw = bbox[2] - bbox[0]
        draw.text((left + (30 - tw) / 2, 14), symbol, font=TITLE_FONT, fill=BLACK)

    beveled_rect(draw, (10, 61, 889, 326), TEAL, raised=False, width=3)
    draw.rectangle((18, 69, 881, 318), fill="#0a8b8b")

    beveled_rect(draw, (10, 333, 889, 360), GRAY, raised=False, width=2)
    draw.text((20, 338), "READY", font=STATUS_FONT, fill=BLACK)
    return window


class GifAnimation:
    def __init__(self, path: Path) -> None:
        image = Image.open(path)
        self.frames: list[Image.Image] = []
        self.durations: list[int] = []
        try:
            while True:
                self.frames.append(image.convert("RGBA").copy())
                self.durations.append(max(20, image.info.get("duration", 100)))
                image.seek(image.tell() + 1)
        except EOFError:
            pass
        self.total_ms = sum(self.durations)

    def frame_at(self, elapsed_ms: int) -> Image.Image:
        cursor = elapsed_ms % self.total_ms
        for frame, duration in zip(self.frames, self.durations):
            if cursor < duration:
                return frame
            cursor -= duration
        return self.frames[-1]


def scaled_clippy(frame: Image.Image, scale: float = 2.0) -> Image.Image:
    size = (
        max(1, round(frame.width * scale)),
        max(1, round(frame.height * scale)),
    )
    return frame.resize(size, Image.Resampling.NEAREST)


def save_sprite_sheet(animations: list[GifAnimation]) -> None:
    sample_times = (850, 1050, 700, 1650)
    sheet = Image.new("RGBA", (4 * 240, 210), (0, 0, 0, 0))
    for index, (animation, sample_time) in enumerate(zip(animations, sample_times)):
        sprite = scaled_clippy(animation.frame_at(sample_time), 2.0)
        x = index * 240 + (240 - sprite.width) // 2
        y = (210 - sprite.height) // 2
        sheet.alpha_composite(sprite, (x, y))
    sheet.save(SPRITE_PATH, optimize=True)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=BODY_FONT) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def bubble_layer(message: str, opacity: int = 255) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    box = (82, 127, 699, 304)
    draw.rounded_rectangle(box, radius=16, fill=CREAM, outline=BLACK, width=3)
    draw.polygon(
        ((696, 241), (752, 276), (696, 282)),
        fill=CREAM,
        outline=BLACK,
    )
    draw.line((696, 243, 696, 280), fill=CREAM, width=6)

    lines = wrap_text(draw, message, 560)
    line_height = 35
    block_height = len(lines) * line_height
    y = 127 + (177 - block_height) / 2 - 2
    for line in lines:
        draw.text((111, y), line, font=BODY_FONT, fill=BLACK)
        y += line_height

    if opacity < 255:
        alpha = layer.getchannel("A").point(lambda value: value * opacity // 255)
        layer.putalpha(alpha)
    return layer


def scene(
    window: Image.Image,
    *,
    assistant: Image.Image | None = None,
    assistant_y: int = 145,
    assistant_scale: float = 1.0,
    assistant_opacity: int = 255,
    assistant_rotation: float = 0,
    message: str | None = None,
    bubble_opacity: int = 255,
) -> Image.Image:
    frame = draw_desktop()
    frame.alpha_composite(window, (30, 25))
    if assistant is not None:
        pose = scaled_clippy(assistant, 2.0)
        if assistant_scale != 1:
            size = (
                max(1, round(pose.width * assistant_scale)),
                max(1, round(pose.height * assistant_scale)),
            )
            pose = pose.resize(size, Image.Resampling.NEAREST)
        if assistant_rotation:
            pose = pose.rotate(
                assistant_rotation,
                resample=Image.Resampling.BICUBIC,
                expand=True,
            )
        if assistant_opacity < 255:
            pose = pose.copy()
            alpha = pose.getchannel("A").point(
                lambda value: value * assistant_opacity // 255
            )
            pose.putalpha(alpha)
        x = 813 - pose.width // 2
        frame.alpha_composite(pose, (x, assistant_y))
    if message is not None:
        frame.alpha_composite(bubble_layer(message, bubble_opacity))
    return frame.convert("RGB")


def scaled_window_frame(window: Image.Image, progress: float) -> Image.Image:
    frame = draw_desktop()
    eased = ease_in_out(progress)
    scale_x = max(0.02, eased)
    scale_y = max(0.02, ease_in_out(min(1, progress * 1.25)))
    scaled = window.resize(
        (max(1, round(window.width * scale_x)), max(1, round(window.height * scale_y))),
        Image.Resampling.NEAREST,
    )
    frame.alpha_composite(
        scaled,
        ((WIDTH - scaled.width) // 2, (HEIGHT - scaled.height) // 2),
    )
    return frame.convert("RGB")


def render(motivation_index: int) -> tuple[list[Image.Image], list[int]]:
    animations = [
        GifAnimation(CLIPPY_DIR / f"clippyani{index}.gif")
        for index in range(1, 8)
    ]
    save_sprite_sheet([animations[index] for index in (0, 1, 3, 6)])
    window = draw_window()
    frames: list[Image.Image] = []
    durations: list[int] = []
    frame_ms = 100
    profile_animation_indexes = (0, 1, 3, 0, 4, 6)
    phases = []
    for message_index, animation_index in enumerate(profile_animation_indexes):
        start = 2.0 + message_index * 3.7
        phases.append((start, start + 3.4, message_index, animation_index))

    profile_end = phases[-1][1]
    quote_intro_start = profile_end + 0.3
    quote_intro_end = quote_intro_start + 3.0
    motivation_start = quote_intro_end + 0.3
    motivation_end = motivation_start + 3.6
    exit_end = motivation_end + 1.0
    close_end = exit_end + 1.0
    total_seconds = close_end + 0.4
    motivation, motivation_animation_number = MOTIVATIONS[motivation_index]
    motivation_animation_index = motivation_animation_number - 1

    for frame_index in range(round(total_seconds * 10)):
        seconds = frame_index / 10
        if frame_index == 0:
            frame = draw_desktop().convert("RGB")
        elif seconds < 1:
            frame = scaled_window_frame(window, seconds)
        elif seconds < 2:
            progress = seconds - 1
            frame = scene(
                window,
                assistant=animations[0].frame_at(round(progress * 1000)),
                assistant_y=round(324 - 179 * ease_out_back(progress)),
                assistant_scale=0.35 + 0.65 * ease_out_back(progress),
                assistant_opacity=round(255 * progress),
                assistant_rotation=360 * (1 - progress),
            )
        elif seconds < profile_end:
            active = None
            for start, end, message_index, animation_index in phases:
                if start <= seconds < end:
                    active = (start, message_index, animation_index)
                    break
            if active is not None:
                start, message_index, animation_index = active
                local_ms = round((seconds - start) * 1000)
                bubble_alpha = min(255, round(local_ms / 300 * 255))
                frame = scene(
                    window,
                    assistant=animations[animation_index].frame_at(local_ms),
                    message=MESSAGES[message_index],
                    bubble_opacity=bubble_alpha,
                )
            else:
                # A short empty-bubble beat prevents text overlap while the
                # authentic source animation switches to the next sequence.
                next_index = next(
                    (
                        animation_index
                        for start, _, _, animation_index in phases
                        if start > seconds
                    ),
                    profile_animation_indexes[-1],
                )
                frame = scene(
                    window,
                    assistant=animations[next_index].frame_at(0),
                    message="",
                )
        elif seconds < quote_intro_end:
            local_ms = round((seconds - quote_intro_start) * 1000)
            frame = scene(
                window,
                assistant=animations[3].frame_at(max(0, local_ms)),
                message=QUOTE_INTRO if seconds >= quote_intro_start else "",
                bubble_opacity=min(255, max(0, round(local_ms / 300 * 255))),
            )
        elif seconds < motivation_start:
            frame = scene(
                window,
                assistant=animations[motivation_animation_index].frame_at(0),
                message="",
            )
        elif seconds < motivation_end:
            local_ms = round((seconds - motivation_start) * 1000)
            frame = scene(
                window,
                assistant=animations[motivation_animation_index].frame_at(local_ms),
                message=motivation,
                bubble_opacity=min(255, round(local_ms / 300 * 255)),
            )
        elif seconds < exit_end:
            progress = seconds - motivation_end
            frame = scene(
                window,
                assistant=animations[motivation_animation_index].frame_at(
                    round(progress * 1000)
                ),
                assistant_y=round(145 + 179 * ease_in_out(progress)),
                assistant_scale=1 - 0.65 * progress,
                assistant_opacity=round(255 * (1 - progress)),
                assistant_rotation=-360 * progress,
            )
        elif seconds < close_end:
            frame = scaled_window_frame(window, 1 - (seconds - exit_end))
        else:
            frame = draw_desktop().convert("RGB")
        frames.append(frame)
        durations.append(frame_ms)
    return frames, durations


def save_contact_sheet(frames: list[Image.Image]) -> None:
    picks = [30, 67, 104, 141, 178, 215, 252, 278]
    thumb_size = (480, 210)
    sheet = Image.new("RGB", (960, 840), "#20242a")
    draw = ImageDraw.Draw(sheet)
    for index, frame_index in enumerate(picks):
        thumb = frames[frame_index].resize(thumb_size, Image.Resampling.LANCZOS)
        x = (index % 2) * 480
        y = (index // 2) * 210
        sheet.paste(thumb, (x, y))
        draw.rectangle((x + 8, y + 8, x + 68, y + 32), fill="#000000")
        draw.text((x + 15, y + 10), f"{frame_index:02}", font=TINY_FONT, fill="white")
    sheet.save(CONTACT_SHEET_PATH, optimize=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--motivation-seed",
        default="james-github-profile-v1",
        help="Reproducible seed used to select the closing motivation.",
    )
    parser.add_argument(
        "--motivation-index",
        type=int,
        choices=range(len(MOTIVATIONS)),
        help="Select a specific zero-based motivation instead of using the seed.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    motivation_index = (
        args.motivation_index
        if args.motivation_index is not None
        else random.Random(args.motivation_seed).randrange(len(MOTIVATIONS))
    )
    frames, durations = render(motivation_index)
    palette_source = frames[30].quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    palette = palette_source.getpalette()
    quantized: list[Image.Image] = []
    for frame in frames:
        converted = frame.quantize(palette=palette_source, dither=Image.Dither.NONE)
        converted.putpalette(palette)
        quantized.append(converted)

    quantized[0].save(
        OUTPUT_PATH,
        save_all=True,
        append_images=quantized[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=1,
    )
    save_contact_sheet(frames)
    print(
        f"Wrote {OUTPUT_PATH.relative_to(ROOT)}: "
        f"{len(frames)} frames, {sum(durations) / 1000:.2f}s"
    )
    print(f"Motivation #{motivation_index}: {MOTIVATIONS[motivation_index][0]}")
    print(f"Wrote preview contact sheet: {CONTACT_SHEET_PATH}")


if __name__ == "__main__":
    main()
