# RUNBOOK.md — robot setup / ops

**Updated:** 2026-11-06 (two live programs; `tm save` / `tm rec`). Tanush's robot: **AIM-4A8B6118**.

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
| `tm boxes` / `tm seg` / `tm both` | the boxes (default; yellow = orange barrel, green = blue, 1 px) / the segmentation tint / both |
| `tm save` | writes the current raw frame as `snapshots/robot_snapN.png` under `barrels/live/` (the camera viewer's naming; N continues past existing files, never overwrites) |
| `tm rec` | writes every frame for ten seconds (at most ten a second) into `snapshots/rec_<stamp>/frame_NNN.png` + `frames.json` (time and frame count per file) |
| `tm raw` | BarrelTracker only: also draw this frame's own boxes in white, to compare with the persisting ones |

- The console prints one line when the number of barrels shown changes, one when a frame is saved, one when a recording finishes.
- `snapshots/` is gitignored. **Import the keepers right away:** `python barrels/tools/import_snaps.py --src barrels/live/snapshots --light … --surface … --scenes …` (`DATA.md`); delete a bad `robot_snapN.png` before importing. Do not mix `tm save` with the camera viewer's `s` key in one session: the viewer's counter restarts at 0 and would overwrite. Recordings are for replaying the multi-frame view offline; keep the folder until that is done.
- Both programs run the detector exactly as `tools/detect_image.py` does (same frozen model, detector, camera preset); ≈ 60 ms per frame on the laptop. The 3-of-4 rule is `src/barrels/tracker.py` (`TrackConfig`); saving is `src/barrels/capture.py`.
- `simple_cli` must be started **from `barrels/live/`**: it imports the program and `barrel_live.py` (what the two share) from the current directory. From elsewhere: `simple_cli`, then `cd` there and `runfsm('BarrelViewer')`.
- Quit with **Ctrl+\** before powering the robot off (below). If the window stops updating, `restart img_thread` at the prompt restarts the camera stream.
- Edit → test cycle: change the `.fsm`, run `genfsm` again, then `runfsm('BarrelViewer')` at the prompt (reloads that module; a change to `barrel_live.py` needs `simple_cli` restarted). If `simple_cli` warns that the `.py` is older than the `.fsm`, you forgot `genfsm`.

## Networking

- **Home wifi:** the robot joins home wifi; the IP is **NOT reserved**, so check the robot's Settings → Radio → Station each time (was 10.0.0.90). Optional fix: reserve it in the Xfinity router (10.0.0.1 → Connected Devices → Add Device with Reserved IP; Station MAC starts `F4:12:FA`).
- **Campus:** `export ROBOT=AIM-4A8B6118.wifi.local.cmu.edu` (worked 9/30, before the home-wifi setup; recheck).
- **AP mode:** robot Settings → Radio → Access Point; join the `AIM-xxxxxxxx` wifi (password `AIM12345`); `ROBOT=192.168.4.1`; no internet while connected.

## Using simple_cli

- Commands go at the `C>` prompt in Terminal: `tm <text>` sends a text message to the running state machine, `show objects`, `show pose`, `show viewer` (camera), `show active` (which nodes run), `runfsm('Name')` (start / reload a program).
- Viewers: camera, world, particle, path (`h` for keys). Camera viewer `s` saves `snapshots/robot_snapN.png` — **the counter resets each session, import immediately** per `DATA.md`.
- **Quit with Ctrl+\ before powering off the robot** — otherwise an endless `ws_status reconnecting` loop + a cv2 crash.

## Noise / known harmless errors

- `ev_poll_posix.cc ... FD from fork parent` gRPC spam is harmless (try `GRPC_VERBOSITY=ERROR`).
- Occasional `ws_status reconnecting` = wifi flakiness.

## FSM programs (aim_fsm)

- `genfsm X.fsm` → `X.py` beside it; `simple_cli X` (from that folder) or `runfsm('X')` at the prompt. The file must define a class named like the module, subclassing `StateMachineProgram`.
- Nodes = actions (`StateNode.start`), transitions = event reactions: `=N=>` immediately, `=C=>` on completion, `=T(secs)=>` timer, `=TM=>` / `=TM('text')=>` on a `tm` message (regex, anchored at the start), `=S=>` / `=F=>` success / failure, `=D=>` data. Nested node classes are referenced as `self.Name()` in `$setup{}` and get `.parent` = the program.
- `robot.camera_image` is the latest 640×480 **RGB** frame; `imshow(name, array)` (from `aim_fsm`) shows an RGB array in a PyQt window and is safe to call from the robot thread; `cv2.imshow` from there is not.
