# RUNBOOK.md — robot setup / ops

**Updated:** 2026-11-19 (the vendor save checked on the robot: it works) · 2026-11-18 (`tm save` also stores the vendor detector's answer) · 2026-11-09 (hs front end is the default; `BARRELS_MODEL`). Tanush's robot: **AIM-4A8B6118**.

## Now — run the live view

```zsh
cd ~/Desktop/Celeste && source setup.zsh        # venv, aim_fsm, simple_cli, ROBOT=192.168.4.1 (AP mode)
# export ROBOT=<ip>                             # only if the robot is on a wifi network instead
ping -c 3 $ROBOT
cd vex-aim-tools/barrels/live && simple_cli BarrelTracker     # or BarrelViewer (per frame, no persistence)
```

At `C>`: `tm boxes` / `tm seg` / `tm both` switch the view (`tm seg`: the main window dims everything that is not a barrel color and a second window shows only the segmented pixels); `tm save` writes a raw frame to `snapshots/` together with what the vendor detector reported for it (`robot_snapN_vendor.json`, and `robot_snapN_vendor.png` to look at); `tm rec` records ten seconds; `tm raw` (tracker) overlays the per-frame boxes. Quit with **Ctrl+\** before powering the robot off. Save a frame of anything that looks wrong and say which file.

---

## Standard startup

```zsh
cd ~/Desktop/Celeste
source setup.zsh                 # venv + PYTHONPATH (aim_fsm, the websocket library) + genfsm/simple_cli on PATH + ROBOT=192.168.4.1
export ROBOT=<ip>                # AFTER sourcing, if not in AP mode
ping -c 3 $ROBOT
cd vex-aim-tools
simple_cli                       # or: simple_cli Celeste / simple_cli Lab6a
```

`setup.zsh` lives outside the repo (it holds credentials); never commit it.

## The live barrel feed (`barrels/live/`)

Two programs, same detector, same commands; pick one:

```zsh
cd ~/Desktop/Celeste/vex-aim-tools/barrels/live
simple_cli BarrelViewer          # the per-frame answer, once a second: what tools/detect_image.py would say about each frame
simple_cli BarrelTracker         # boxes that persist: a barrel is shown after 3 of the last 4 frames agree (5 frames a second)
genfsm BarrelViewer.fsm          # only after editing a .fsm — rewrites the .py next to it (both .py files are committed)
```

**Swapping the front end** (2026-11-09): the default is the hs model (`results/2026-11-09_hs_candidate/config.json`, adopted 2026-11-09). Set `BARRELS_MODEL` to another results `config.json` that carries a fitted model and both programs and `tools/detect_image.py` use that instead; e.g. the old v1 front end for a side-by-side: `export BARRELS_MODEL=~/Desktop/Celeste/vex-aim-tools/barrels/results/2026-10-20_v1_test_adaptive/config.json` before `simple_cli`; `unset BARRELS_MODEL` to go back. The program prints which model it loaded when it is not the default.

At the `C>` prompt (both programs):

| command | does |
|---|---|
| `tm boxes` / `tm seg` / `tm both` | the boxes (default; yellow = orange barrel, green = blue, 1 px) / the segmentation: the main window dims every pixel not classified orange or blue (barrel-colored pixels stay at full brightness) and a second window, `barrels seg` or `barrels (tracked) seg`, shows only the classified pixels in their class color on black / the seg pair with the boxes on the main window. `tm boxes` closes the second window (within one refresh) |
| `tm save` | writes the current raw frame as `snapshots/robot_snapN.png` under `barrels/live/` (the camera viewer's naming; N continues past existing files, never overwrites), and next to it `robot_snapN_vendor.json` (the vendor detector's object list for that frame) and `robot_snapN_vendor.png` (a copy of the frame with the vendor's boxes drawn; the raw frame is never drawn on). The console line ends with `vendor: 2 objects (OrangeBarrel, BlueBarrel)` or `vendor NOT available (reason)`; the frame is saved either way |
| `tm rec` | writes every frame for ten seconds (at most ten a second) into `snapshots/rec_<stamp>/frame_NNN.png` + `frames.json` (time, frame count and the vendor detector's answer per file) |
| `tm raw` | BarrelTracker only: also draw this frame's own boxes in white, to compare with the persisting ones |

- The console prints one line when the number of barrels shown changes, one when a frame is saved, one when a recording finishes.
- `snapshots/` is gitignored. **Import the keepers right away:** `python barrels/tools/import_snaps.py --src barrels/live/snapshots --light … --surface … --scenes …` (`DATA.md`); delete a bad `robot_snapN.png` before importing. Do not mix `tm save` with the camera viewer's `s` key in one session: the viewer's counter restarts at 0 and would overwrite. Recordings are for replaying the multi-frame view offline; keep the folder until that is done.
- Both programs run the detector exactly as `tools/detect_image.py` does (same frozen model, detector, camera preset); ≈ 60 ms per frame on the laptop. The 3-of-4 rule is `src/barrels/tracker.py` (`TrackConfig`); saving is `src/barrels/capture.py`.
- `simple_cli` must be started **from `barrels/live/`**: it imports the program and `barrel_live.py` (what the two share) from the current directory. From elsewhere: `simple_cli`, then `cd` there and `runfsm('BarrelViewer')`.
- Quit with **Ctrl+\** before powering the robot off (below). If the window stops updating, `restart img_thread` at the prompt restarts the camera stream.
- Edit → test cycle: change the `.fsm`, run `genfsm` again, then `runfsm('BarrelViewer')` at the prompt (reloads that module; a change to `barrel_live.py` needs `simple_cli` restarted). If `simple_cli` warns that the `.py` is older than the `.fsm`, you forgot `genfsm`.

## The vendor detector's answer with every frame (2026-11-18; checked on the robot 2026-11-19)

The robot's built-in detector ("aivision") runs on the robot all the time and its object list arrives in every status packet (about 20 a second): `robot.robot0.status['aivision']['objects']` = `{count, items}`; each item has `type_str` (`aiobj` for a model object, `tag` for an AprilTag), `id` (0 SportsBall, 1 BlueBarrel, 2 OrangeBarrel, 3 Robot), `name`, `originx`, `originy`, `width`, `height` (top-left corner and size, in **320×240** units: multiply by 2 for our 640×480 frame) and `score`. Nothing has to be requested or switched on, so reading it does not slow the image stream (tag detection, the slow one, stays off).

`tm save` pairs each camera frame with the list that was current when the frame arrived and writes the three files of the table above. `barrels/tools/import_snaps.py` then moves the `.json` to `barrels/data/vendor/<stem>_vendor.json` under the frame's new name (the dry run shows it; the `_vendor.png` look-at copies stay in `snapshots/`, delete them when done). Schema: `DATA.md`, "Vendor detections". Once the frames are imported, assigned to a split and boxed: `python barrels/tools/report.py --vendor` scores the vendor next to our detector on those frames (`HOW-IT-WORKS.md` §4).

**First live check (once, before the first shoot that relies on it):**

1. Start `simple_cli BarrelTracker`, put one orange and one blue barrel at about 20 cm, `tm save`. Expected console line: `BarrelTracker: saved snapshots/robot_snapN.png | vendor: 2 objects (OrangeBarrel, BlueBarrel)`. If it says `vendor NOT available (...)`, send the reason.
2. Open `snapshots/robot_snapN_vendor.png`: one box around each barrel, orange on the orange barrel and blue on the blue one, each tight on its barrel (not shifted, not half size). Compare with the robot's own screen or `show viewer` (the camera viewer draws the vendor's boxes live).
3. Open `snapshots/robot_snapN_vendor.json`: `"available": true`, two objects, `"read_at": "frame"`, and `raw` holds the robot's own fields. Note what `score` looks like (0–100?).
4. Empty table, `tm save`: `vendor: 0 objects`, and `"available": true, "objects": []` in the file.
5. Timing: with the barrels in view, move one quickly and `tm save` while it moves; in the `_vendor.png` the box may trail or lead the barrel by a little. For still scenes (every planned shot) this does not matter; say how large it is.
6. The stream is not slowed: the tracker window updates as fast as before, and `tm rec` writes about as many frames in ten seconds as it did before (the 2026-11-16 recordings have 49 and 51 files).
7. `python barrels/tools/import_snaps.py --src barrels/live/snapshots --light test --surface test --scenes core,neg --dry-run`: each line shows the frame's new name and `+ data/vendor/<stem>_vendor.json`.

**Result of the first live check, 2026-11-19 (Tanush with the data session, on the black ottoman lid):** steps 1 to 4 pass. The console line ends with the vendor's objects, the `.json` says `"available": true` and `"read_at": "frame"`, the boxes in `_vendor.png` sit tight on the right barrels (not shifted, not half size), `score` runs 0 to 100 (98 and 99 seen), and an empty frame gives `0 objects`. Step 7: the importer carried all 36 vendor files of the first shoot under the frames' new names. Not done: step 5 (a moving barrel) and step 6 (the stream speed). Seen in passing: `tm save` starts again at `robot_snap0` when the top level of `snapshots/` holds no `robot_snapN.png`, so move a finished session's files into a subfolder, never mix two sessions there; the camera's auto exposure darkens the whole frame when a hand comes in, so wait about three seconds after the hand is out.

## Networking

- **Home wifi:** the robot joins home wifi; the IP is **NOT reserved**, so check the robot's Settings → Radio → Station each time (was 10.0.0.90). Optional fix: reserve it in the Xfinity router (10.0.0.1 → Connected Devices → Add Device with Reserved IP; Station MAC starts `F4:12:FA`).
- **Campus:** `export ROBOT=AIM-4A8B6118.wifi.local.cmu.edu` (worked 9/30, before the home-wifi setup; recheck).
- **AP mode:** robot Settings → Radio → Access Point; join the `AIM-xxxxxxxx` wifi (password `AIM12345`); `ROBOT=192.168.4.1`; no internet while connected.

## Using simple_cli

- Commands go at the `C>` prompt in Terminal: `tm <text>` sends a text message to the running state machine, `show objects`, `show pose`, `show viewer` (camera), `show active` (which nodes run), `runfsm('Name')` (start / reload a program).
- Viewers: camera, world, particle, path (`h` for keys). Camera viewer `s` saves `snapshots/robot_snapN.png`, `S` (shift) saves `snapshots/robot_asnapN.png`, the picture with the vendor's boxes and the crosshairs drawn on it (a picture only, no numbers; both keys share one counter) — **the counter resets each session, import immediately** per `DATA.md`.
- **Quit with Ctrl+\ before powering off the robot** — otherwise an endless `ws_status reconnecting` loop + a cv2 crash.

## Noise / known harmless errors

- `ev_poll_posix.cc ... FD from fork parent` gRPC spam is harmless (try `GRPC_VERBOSITY=ERROR`).
- Occasional `ws_status reconnecting` = wifi flakiness.

## FSM programs (aim_fsm)

- `genfsm X.fsm` → `X.py` beside it; `simple_cli X` (from that folder) or `runfsm('X')` at the prompt. The file must define a class named like the module, subclassing `StateMachineProgram`.
- Nodes = actions (`StateNode.start`), transitions = event reactions: `=N=>` immediately, `=C=>` on completion, `=T(secs)=>` timer, `=TM=>` / `=TM('text')=>` on a `tm` message (regex, anchored at the start), `=S=>` / `=F=>` success / failure, `=D=>` data. Nested node classes are referenced as `self.Name()` in `$setup{}` and get `.parent` = the program.
- `robot.camera_image` is the latest 640×480 **RGB** frame; `imshow(name, array)` (from `aim_fsm`) shows an RGB array in a PyQt window and is safe to call from the robot thread; `cv2.imshow` from there is not.
