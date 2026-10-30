# Beam

Wirelessly share and install badge applications peer-to-peer by holding badges back-to-back.

## Overview

Beam sends an app from one badge to another over Bluetooth Low Energy. You don't need a computer or Wi-Fi. The receiving badge writes the files to `/apps/<slug>` on its flash, and the app then shows up in Beam's Installed tab and the badge menu.

The app list has two tabs:

- **Share** lists every app on the badge that Beam can send, from `/system/apps` and `/apps`.
- **Installed** lists apps that arrived over Beam, from `/apps`.

The header shows how much free flash the badge has.

## How to use

1. Open Beam on both badges.
2. On the sending badge, pick an app on the Share tab and press SELECT.
3. Hold the two badges back to back. The case lights pulse while they pair, and a bar fills as the link gets stronger.
4. The transfer starts on its own once the link is up.
5. The receiving badge launches the new app after 4 seconds. Press SELECT to launch it right away, or BACK to stay in Beam.

## Controls

| Screen          | Button       | Action                                                |
| --------------- | ------------ | ----------------------------------------------------- |
| App list        | LEFT / RIGHT | Switch to the Share / Installed tab                   |
| App list        | UP / DOWN    | Move through the current tab                          |
| App list        | SELECT       | Send the app (Share tab) or launch it (Installed tab) |
| App list        | BACK         | Exit Beam                                             |
| Waiting to pair | BACK or LEFT | Cancel and go back to the list                        |
| Transferring    | BACK         | Cancel the transfer                                   |
| Received        | SELECT       | Launch the new app now                                |
| Received        | BACK         | Close and go back to the list                         |

## Limits

- An app can be at most 250 KB.
- Beam won't send `menu`, `startup`, `mass_storage` or itself.
- It skips dotfiles and `__pycache__` folders.
- The receiving badge checks it has room before it accepts the app.
- In `__init__.py`, Beam rewrites `/system/apps/<slug>` paths to `/apps/<slug>`, so apps that use absolute asset paths still find their files.

## Size

37 KB (38,638 bytes) on the badge, not counting `__pycache__`.

## Deploying to the badge

Connect the badge over USB and run this from the repo root:

```bash
python3 .github/skills/hyb26-skill/scripts/badge_serial.py disk-mode
python3 .github/skills/hyb26-skill/scripts/deploy_app.py badge/apps/beam --replace --write
python3 .github/skills/hyb26-skill/scripts/badge_serial.py eject
```

If the app is already on the badge, `--replace` backs up the old copy to `BADGER/.badge-app-backups/` first. Leave out `--write` to see what would be copied without copying it.

## Hardware requirements

- The onboard Raspberry Pi RM2 wireless module, which Beam drives through `badgeware.link`.
