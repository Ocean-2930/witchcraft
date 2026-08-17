#!/usr/bin/env python3
"""Propagate opaque edge colors into low-alpha PNG pixels without changing alpha."""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

from PIL import Image


NEIGHBORS = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1))


def pixel_data(image: Image.Image):
    if hasattr(image, "get_flattened_data"):
        return image.get_flattened_data()
    return image.getdata()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="RGBA PNG input")
    parser.add_argument("--output", type=Path, help="output PNG; defaults to <stem>-alpha-bleed.png")
    parser.add_argument("--radius", type=int, default=8, help="maximum RGB propagation distance (default: 8)")
    parser.add_argument(
        "--edge-alpha",
        type=int,
        default=64,
        help="replace RGB where alpha is at or below this value (default: 64)",
    )
    parser.add_argument("--check", action="store_true", help="report alpha and matte statistics without writing")
    return parser.parse_args()


def load_rgba(path: Path) -> Image.Image:
    image = Image.open(path)
    if image.format != "PNG" or "A" not in image.getbands():
        raise SystemExit(f"error: {path} must be a PNG with a real alpha channel; got {image.mode}")
    return image.convert("RGBA")


def suspicious_ratio(image: Image.Image, edge_alpha: int) -> tuple[int, float]:
    suspicious = 0
    edge_count = 0
    for red, green, blue, alpha in pixel_data(image):
        if not 0 < alpha <= edge_alpha:
            continue
        edge_count += 1
        spread = max(red, green, blue) - min(red, green, blue)
        if (min(red, green, blue) >= 220 or max(red, green, blue) <= 24) and spread <= 16:
            suspicious += 1
    return edge_count, suspicious / edge_count if edge_count else 0.0


def bleed(image: Image.Image, radius: int, edge_alpha: int) -> Image.Image:
    if radius < 1:
        raise SystemExit("error: --radius must be at least 1")
    if not 0 <= edge_alpha < 255:
        raise SystemExit("error: --edge-alpha must be between 0 and 254")

    width, height = image.size
    source = list(pixel_data(image))
    result = source.copy()
    distance = [-1] * (width * height)
    nearest_rgb: list[tuple[int, int, int] | None] = [None] * (width * height)
    queue: deque[int] = deque()

    for index, (red, green, blue, alpha) in enumerate(source):
        if alpha > edge_alpha:
            distance[index] = 0
            nearest_rgb[index] = (red, green, blue)
            queue.append(index)

    while queue:
        index = queue.popleft()
        current_distance = distance[index]
        if current_distance >= radius:
            continue
        x = index % width
        y = index // width
        for offset_x, offset_y in NEIGHBORS:
            neighbor_x = x + offset_x
            neighbor_y = y + offset_y
            if not (0 <= neighbor_x < width and 0 <= neighbor_y < height):
                continue
            neighbor = neighbor_y * width + neighbor_x
            if distance[neighbor] != -1:
                continue
            distance[neighbor] = current_distance + 1
            nearest_rgb[neighbor] = nearest_rgb[index]
            queue.append(neighbor)

    for index, (_, _, _, alpha) in enumerate(source):
        replacement = nearest_rgb[index]
        if alpha <= edge_alpha and replacement is not None and 0 < distance[index] <= radius:
            result[index] = (*replacement, alpha)

    output = Image.new("RGBA", image.size)
    output.putdata(result)
    return output


def main() -> None:
    args = parse_args()
    image = load_rgba(args.input)
    edge_count, ratio = suspicious_ratio(image, args.edge_alpha)
    print(f"input={args.input} size={image.width}x{image.height} edge_pixels={edge_count} suspicious_ratio={ratio:.4f}")
    if args.check:
        return

    output_path = args.output or args.input.with_name(f"{args.input.stem}-alpha-bleed.png")
    cleaned = bleed(image, args.radius, args.edge_alpha)
    if list(pixel_data(image.getchannel("A"))) != list(pixel_data(cleaned.getchannel("A"))):
        raise SystemExit("error: alpha integrity check failed")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.save(output_path, format="PNG")
    cleaned_edge_count, cleaned_ratio = suspicious_ratio(cleaned, args.edge_alpha)
    print(
        f"output={output_path} edge_pixels={cleaned_edge_count} "
        f"suspicious_ratio={cleaned_ratio:.4f} alpha_unchanged=true"
    )


if __name__ == "__main__":
    main()
