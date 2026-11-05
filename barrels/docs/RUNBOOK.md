# RUNBOOK.md — robot setup / ops

**Updated:** 2026-11-05 (the live feed). Tanush's robot: **AIM-4A8B6118**.

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

## The live barrel feed (`barrels/live/BarrelViewer.fsm`)

```zsh
cd ~/Desktop/Celeste/vex-aim-tools/barrels/live
genfsm BarrelViewer.fsm          # only after editing the .fsm — writes BarrelViewer.py next to it (committed)
simple_cli BarrelViewer          # connects, starts the machine; a window "barrels" opens after the first frame
```

- Once a second the robot's image is shown with our boxes: **yellow = orange barrel, green = blue barrel**, 1 px. The console prints one line when the barrel count changes.
- At the `C>` prompt: `tm seg` shows the color segmentation blended over the image (orange / blue tint = what the front end calls barrel), `tm boxes` goes back to the boxes, `tm both` shows both.
- It runs the detector exactly as `tools/detect_image.py` does (same frozen model, same detector, same camera preset); a frame takes ≈ 60 ms on the laptop.
- `simple_cli` must be started **from `barrels/live/`**: it imports the program from the current directory. From anywhere else: `simple_cli` then `runfsm('BarrelViewer')` after `cd`-ing there, or add the folder to `PYTHONPATH`.
- To grab the frame you are looking at as a PNG, `show viewer` opens the camera viewer and `s` saves `snapshots/robot_snapN.png` (rename / import per `DATA.md`). The live window itself has no save key.
- Quit with **Ctrl+\** before powering the robot off (below). If the window stops updating, `restart img_thread` at the prompt restarts the camera stream.
- Edit → test cycle: change the `.fsm`, run `genfsm` again, then `runfsm('BarrelViewer')` at the prompt (reloads the module). If `simple_cli` warns that the `.py` is older than the `.fsm`, you forgot `genfsm`.

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
