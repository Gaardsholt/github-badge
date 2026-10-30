# Patch AI

Meet Patch AI, your cheerful Bestseller Tech denim robot companion on the GitHub Universe 2026 badge.

## Usage

Launch Patch AI from the badge menu. Patch AI bobs up and down, blinks its stitched button eyes every few seconds, and has a power button that pulses with a cyan glow.

### Modes

- **Waving** is the default. Patch AI bobs gently and waves.
- **Dancing** bobs higher and faster, and waves faster too.
- **Standby** barely moves, rests its arm at its side and keeps its eyes open.

The current mode is shown in the top right corner.

### Controls

- **SELECT**: Patch AI says a random greeting. In Waving mode it also does a Super Wave, waving almost twice as fast for 3 seconds.
- **LEFT / RIGHT**: Switch mode. The new mode name pops up in a speech bubble.
- **BACK**: Go back to the badge menu.

No extra hardware, network connection or secrets needed.

## Size

124 KB (126,746 bytes) on the badge, not counting `__pycache__`. That's under [Beam](../beam/README.md)'s 250 KB limit, so you can beam it to another badge.

## Deploying to the badge

Connect the badge over USB and run this from the repo root:

```bash
python3 .github/skills/hyb26-skill/scripts/badge_serial.py disk-mode
python3 .github/skills/hyb26-skill/scripts/deploy_app.py badge/apps/patch_ai --replace --write
python3 .github/skills/hyb26-skill/scripts/badge_serial.py eject
```

If the app is already on the badge, `--replace` backs up the old copy to `BADGER/.badge-app-backups/` first. Leave out `--write` to see what would be copied without copying it.

## Rebuilding the images

The images in `assets/`, `icon.png` and `metrics.py` are all generated from `tools/assets/patch_ai/character_clean.png`. Edit that file, then run this from the repo root:

```bash
python3 -m pip install Pillow
python3 tools/build_patch_ai_assets.py
```

Don't edit `metrics.py` by hand. The next build overwrites it.
