#!/usr/bin/env python3
"""Build Patch AI character assets for the Universe 2026 badge."""

import math
from pathlib import Path
from PIL import Image, ImageDraw

REPO_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = REPO_ROOT / "badge/apps/patch_ai"
ASSETS_DIR = APP_DIR / "assets"
SOURCE_IMAGE = REPO_ROOT / "tools/assets/patch_ai/character_clean.png"

# Arms touch the body, so they are split along hand-traced source columns.
# Arm and body both keep the shared outline so each part has an edge of its own.
ARM_TOP = 284
LEFT_ARM_CUT = [(284, 141), (500, 141), (510, 136)]  # arm keeps x < cut
LEFT_BODY_CUT = [(284, 134), (505, 134), (506, 136)]  # body drops x < cut
RIGHT_ARM_CUT = [(284, 711)]  # arm keeps x >= cut
RIGHT_BODY_CUT = [(284, 713)]  # body drops x >= cut


def cut_at(points, y):
    if y <= points[0][0]:
        return points[0][1]
    for (y0, x0), (y1, x1) in zip(points, points[1:]):
        if y <= y1:
            return round(x0 + (x1 - x0) * (y - y0) / (y1 - y0))
    return points[-1][1]


def columns(side, cut, width):
    return range(0, cut) if side == "left" else range(cut, width)


def split_arm(src, body, side, arm_cut, body_cut):
    """Move one arm out of `body` into a full-size layer and return it."""
    w, h = src.size
    arm = Image.new("RGBA", src.size, (0, 0, 0, 0))
    src_px, arm_px, body_px = src.load(), arm.load(), body.load()
    for y in range(ARM_TOP, h):
        for x in columns(side, cut_at(arm_cut, y), w):
            arm_px[x, y] = src_px[x, y]
        for x in columns(side, cut_at(body_cut, y), w):
            body_px[x, y] = (0, 0, 0, 0)
    return arm


def build():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    if not SOURCE_IMAGE.exists():
        raise FileNotFoundError(f"Source image not found: {SOURCE_IMAGE}")

    src = Image.open(SOURCE_IMAGE).convert("RGBA")
    w, h = src.size

    # 1. Scale & Geometry:
    target_height = 170
    scale = target_height / h
    target_width = int(w * scale)

    shoulder_src_x = 138
    shoulder_src_y = 315

    # 3. Split both arms off the body (arms are drawn in front)
    body_img = src.copy()
    left_arm = split_arm(src, body_img, "left", LEFT_ARM_CUT, LEFT_BODY_CUT)
    right_arm = split_arm(src, body_img, "right", RIGHT_ARM_CUT, RIGHT_BODY_CUT)

    # Square crop wide enough for the whole head (source x 119..713); arms left out
    icon = body_img.crop((106, 0, 726, 620)).resize((48, 48), Image.Resampling.LANCZOS)
    icon.save(APP_DIR / "icon.png", optimize=True)
    print("Saved icon.png (48x48)")

    size = (target_width, target_height)
    scaled_body = body_img.resize(size, Image.Resampling.LANCZOS)
    scaled_body.save(ASSETS_DIR / "body.png", optimize=True)
    print(f"Saved body.png: {scaled_body.size}")

    # Arms are scaled at full size first so they line up exactly with the body
    arm_pos = {}
    for name, layer in (("left", left_arm), ("right", right_arm)):
        scaled = layer.resize(size, Image.Resampling.LANCZOS)
        box = scaled.getbbox()
        scaled.crop(box).save(ASSETS_DIR / f"arm_{name}.png", optimize=True)
        arm_pos[name] = box[:2]
        print(f"Saved arm_{name}.png: {box[2] - box[0]}x{box[3] - box[1]} at {box[:2]}")

    # 4. Create waving spritesheet from the left arm
    src_arm = left_arm.crop((0, 270, 155, 635))
    arm_canvas = Image.new("RGBA", (700, 700), (0, 0, 0, 0))
    arm_canvas.paste(src_arm, (350 - 138, 350 - 45), src_arm)

    # 6 wave loop frames (ping-pong cycle: -130 -> -165 -> -130)
    wave_angles = [-130, -137, -148, -158, -165, -150]

    # Crop around shoulder:
    # in source: x from (350 - 240) to (350 + 80) = 320 px
    # y from (350 - 350) to (350 + 40) = 390 px
    # Scaled:
    cell_w = 76
    cell_h = 92
    frames = []
    for a in wave_angles:
        rot = arm_canvas.rotate(a, resample=Image.Resampling.BICUBIC, center=(350, 350))
        crop = rot.crop((350 - 240, 350 - 350, 350 + 80, 350 + 40))
        scaled_frame = crop.resize((cell_w, cell_h), Image.Resampling.LANCZOS)
        frames.append(scaled_frame)

    sheet = Image.new("RGBA", (cell_w * len(frames), cell_h), (0, 0, 0, 0))
    for i, frame in enumerate(frames):
        sheet.paste(frame, (i * cell_w, 0))

    sheet.save(ASSETS_DIR / "arm_sheet.png", optimize=True)
    print(f"Saved arm_sheet.png: {sheet.size} ({len(frames)} frames)")

    # 5. Build compact closed-eye blink overlay (only covers eye band)
    # Eyes in body: lx=70, ly=52; rx=130, ry=52
    blink_w = 90
    blink_h = 32
    blink_x = 55
    blink_y = 38
    blink_overlay = Image.new("RGBA", (blink_w, blink_h), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(blink_overlay)

    eye_radius = int(52 * scale)
    thread_cyan = (68, 204, 218, 255)

    for cx_body, cy_body in [
        (int(298 * scale), int(222 * scale)),
        (int(552 * scale), int(222 * scale)),
    ]:
        cx = cx_body - blink_x
        cy = cy_body - blink_y
        bdraw.ellipse(
            (cx - eye_radius, cy - eye_radius, cx + eye_radius, cy + eye_radius),
            fill=(52, 76, 110, 250),
        )
        arc_box = (
            cx - eye_radius + 4,
            cy - eye_radius + 8,
            cx + eye_radius - 4,
            cy + eye_radius - 2,
        )
        bdraw.arc(arc_box, start=20, end=160, fill=thread_cyan, width=3)
        for angle_deg in range(30, 160, 28):
            rad = math.radians(angle_deg)
            px = cx + int((eye_radius - 6) * math.cos(rad))
            py = cy + int((eye_radius - 8) * math.sin(rad))
            bdraw.line((px - 2, py - 2, px + 2, py + 2), fill=thread_cyan, width=2)

    blink_overlay.save(ASSETS_DIR / "blink.png", optimize=True)
    print(f"Saved compact blink.png: {blink_overlay.size}")

    sh_in_body_x = int(shoulder_src_x * scale)
    sh_in_body_y = int(shoulder_src_y * scale)
    sh_in_cell_x = int(240 * scale)
    sh_in_cell_y = int(350 * scale)

    arm_rel_x = sh_in_body_x - sh_in_cell_x
    arm_rel_y = sh_in_body_y - sh_in_cell_y

    meta = f"""# Auto-generated by tools/build_patch_ai_assets.py
SCALE = {scale:.6f}
BODY_W = {target_width}
BODY_H = {target_height}
ARM_CELL_W = {cell_w}
ARM_CELL_H = {cell_h}
ARM_FRAME_COUNT = {len(wave_angles)}
ARM_REL_X = {arm_rel_x}
ARM_REL_Y = {arm_rel_y}
ARM_LEFT_X = {arm_pos["left"][0]}
ARM_LEFT_Y = {arm_pos["left"][1]}
ARM_RIGHT_X = {arm_pos["right"][0]}
ARM_RIGHT_Y = {arm_pos["right"][1]}
BLINK_X = {blink_x}
BLINK_Y = {blink_y}
POWER_X = {int(423 * scale)}
POWER_Y = {int(448 * scale)}
"""
    (APP_DIR / "metrics.py").write_text(meta)
    print("Saved metrics.py")


if __name__ == "__main__":
    build()
