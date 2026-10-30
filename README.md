# github-badge

My apps for the GitHub Universe 2026 badge. The badge runs MicroPython on an RP2350, and each app is a folder you copy onto it.

## Apps

| App                                                     | What it does                                                                                | Size   |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------ |
| [Beam](badge/apps/beam/README.md)                       | Send an app from one badge to another over Bluetooth by holding them back to back.          | 37 KB  |
| [Mona Teleporter](badge/apps/mona_teleporter/README.md) | Sends the infrared codes for the Mona's Expedition locations, so nearby badges unlock them. | 145 KB |
| [Patch AI](badge/apps/patch_ai/README.md)               | An animated denim robot that waves, dances and naps.                                        | 124 KB |

Mona Teleporter can unlock every location, or wipe all progress, on someone else's badge. Ask before you point it at anyone.

## Install an app

You need a USB-C cable that carries data, not just power.

### Copy it by hand

1. Put the badge in USB Disk Mode. Open the **Mass Storage** app on the badge, or double-tap RESET. A drive called `BADGER` shows up on your computer.
2. Copy the app folder, for example `badge/apps/beam`, into `BADGER/apps`. Some firmware versions use `BADGER/system/apps` instead. Leave out any `__pycache__` folder.
3. Eject `BADGER`. The badge restarts into the menu and the app shows up there.

Never copy anything to the `RP2350` drive. That one is the firmware bootloader.

### Use the deploy script

The scripts in [.github/skills/hyb26-skill/scripts](.github/skills/hyb26-skill/scripts) switch the badge into Disk Mode for you and back up any app they replace. They need Python 3.10+ and `mpremote`:

```bash
python3 -m pip install mpremote
```

Then, from the repo root:

```bash
scripts=".github/skills/hyb26-skill/scripts"
python3 "$scripts/badge_serial.py" disk-mode
python3 "$scripts/deploy_app.py" badge/apps/beam           # dry run, shows what would be copied
python3 "$scripts/deploy_app.py" badge/apps/beam --write   # copy it
python3 "$scripts/badge_serial.py" eject
```

To update an app that's already on the badge, add `--replace`. The old copy goes to `.badge-app-backups`. On Windows, use `python` and backslashes in paths. [SKILL.md](.github/skills/hyb26-skill/SKILL.md) has the full command list.

### App icons in the menu

The stock badge menu ignores each app's `icon.png`. To get the icons, put the badge in Disk Mode and run the menu patch. It's a dry run unless you pass `--write`:

```bash
python3 "$scripts/patch_menu_icons.py"
python3 "$scripts/patch_menu_icons.py" --write
```

## Repository layout

```text
badge/apps/   one folder per app
tools/        build_patch_ai_assets.py, which rebuilds the Patch AI images
.github/      Copilot skill, README check script, PR template
```

## Writing an app

Each app folder needs three files:

- `__init__.py` with the app code.
- `icon.png`, square and at least 24x24. 48x48 looks sharpest.
- `README.md`. The first paragraph after the title must be one sentence of 10 to 200 characters ending in `.`, `!` or `?`. Check it with `python3 .github/scripts/validate_app_readmes.py`.

Run `python3 .github/skills/hyb26-skill/scripts/validate_app.py badge/apps/<app>` for a quick local check. Try the app in the [simulator](https://badger.github.io/editor) before you put it on a badge, then test it on real hardware, since the simulator doesn't match the firmware exactly. Keep `secrets.py` out of git.

## Credits

- [badger/home](https://github.com/badger/home) (MIT): the README check script, the pull request template and the material the Copilot skill references are based on.
- [Gadgetoid's menu icon patch](https://gist.github.com/Gadgetoid/f72b85e6efe603bd02b2b730bbc40356), which `patch_menu_icons.py` applies.
- The [badger.github.io](https://badger.github.io/) simulator and app tools.
- Mona and the GitHub Universe badge belong to GitHub.

## License

MIT. See [LICENSE](LICENSE).
