# Mona Teleporter

Emits infrared beacon signals to simulate Mona's Expedition locations for nearby badges.

Pick a location and the badge sends its code from the IR LEDs on the top edge. A badge running the official Mona's Expedition app that picks up the signal unlocks that location.

## Stations

LEFT and RIGHT step through 11 entries. The first nine are the expedition locations:

| #   | Location            | Code   |
| --- | ------------------- | ------ |
| 1   | Mo's Diner          | `0x11` |
| 2   | Under the Hood      | `0x22` |
| 3   | Creator Cabana      | `0x33` |
| 4   | Open Source Records | `0x44` |
| 5   | Makerspace          | `0x55` |
| 6   | Hack Your Badge     | `0x66` |
| 7   | Demos & Donuts      | `0x77` |
| 8   | Level Up Lounge     | `0x88` |
| 9   | CAB Member          | `0x99` |

The last two are special:

- **Tour: Unlock All** sends all nine codes in a row, about 70 ms apart. The screen counts up "Station X/9" as it goes.
- **Expedition Reset** sends `0xF0`, which wipes the expedition progress on the receiving badge.

Ask before you use either one on someone else's badge. Landing on either entry turns auto mode off and sends nothing, so press SELECT to send it. If you turn auto back on while you're on one of them, it sends every second.

## Controls

| Button       | Action                                                               |
| ------------ | -------------------------------------------------------------------- |
| LEFT / RIGHT | Previous / next entry, and send it once (Tour and Reset aren't sent) |
| SELECT       | Send the current entry now                                           |
| UP / DOWN    | Turn auto mode on or off                                             |

In auto mode the badge repeats the current entry every second. While it transmits, the case LEDs light up and rings spread out from the icon.

## How to tap

1. Pick a location.
2. Leave auto mode on, or press SELECT.
3. Point the top edge of your badge, where the IR LEDs are, at the top edge of the other badge, where its IR receiver is.
4. The other badge plays its unlock animation.

## Size

145 KB (149,251 bytes) on the badge, not counting `__pycache__`. That's under [Beam](../beam/README.md)'s 250 KB limit, so you can beam it to another badge.

## Deploying to the badge

Connect the badge over USB and run this from the repo root:

```bash
python3 .github/skills/hyb26-skill/scripts/badge_serial.py disk-mode
python3 .github/skills/hyb26-skill/scripts/deploy_app.py badge/apps/mona_teleporter --replace --write
python3 .github/skills/hyb26-skill/scripts/badge_serial.py eject
```

If the app is already on the badge, `--replace` backs up the old copy to `BADGER/.badge-app-backups/` first. Leave out `--write` to see what would be copied without copying it.

## Technical details

- Address `0x45`, the Universe beacon address.
- 38 kHz carrier, NEC framing: 9 ms burst, 4.5 ms space, 560 µs bits.
- Each send repeats the code 3 times. Tour mode sends each code twice.
- Sender: two IR LEDs on GPIO 16, switched by a DMN3731U MOSFET. The app uses the firmware's `aye_arr` NEC sender and falls back to its own PIO program if `aye_arr` isn't there.
- Receiver on the other badge: VSOP38338 demodulator on GPIO 17.
