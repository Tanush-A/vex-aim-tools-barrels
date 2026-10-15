# RUNBOOK.md — robot setup / ops

**Updated:** 2026-10-14. Tanush's robot: **AIM-4A8B6118**.

## Standard startup

```zsh
cd ~/Desktop/Celeste
source setup.zsh                 # venv + sets $ROBOT default 192.168.4.1
export ROBOT=<ip>                # AFTER sourcing
ping -c 3 $ROBOT
cd vex-aim-tools
simple_cli                       # or: simple_cli Celeste / simple_cli Lab6a
```

## Networking

- **Home wifi:** the robot joins home wifi; the IP is **NOT reserved**, so check the robot's Settings → Radio → Station each time (was 10.0.0.90). Optional fix: reserve it in the Xfinity router (10.0.0.1 → Connected Devices → Add Device with Reserved IP; Station MAC starts `F4:12:FA`).
- **Campus:** `export ROBOT=AIM-4A8B6118.wifi.local.cmu.edu` (worked 9/30, before the home-wifi setup; recheck).
- **AP mode:** robot Settings → Radio → Access Point; join the `AIM-xxxxxxxx` wifi (password `AIM12345`); `ROBOT=192.168.4.1`; no internet while connected.

## Using simple_cli

- Commands go at the `C>` prompt in Terminal: `tm`, `show objects`, `show pose`.
- Viewers: camera, world, particle, path (`h` for keys). Camera viewer `s` saves `snapshots/robot_snapN.png` — **the counter resets each session, rename immediately** per `DATA.md`.
- **Quit with Ctrl+\ before powering off the robot** — otherwise an endless `ws_status reconnecting` loop + a cv2 crash.

## Noise / known harmless errors

- `ev_poll_posix.cc ... FD from fork parent` gRPC spam is harmless (try `GRPC_VERBOSITY=ERROR`).
- Occasional `ws_status reconnecting` = wifi flakiness.

## FSM programs

- `genfsm X.fsm` → `simple_cli X`.
- aim_fsm: nodes = actions, transitions = event reactions (`=C=>`, `=S=>`, `=F=>`, `=T(n)=>`, `=TM=>`, `=D=>`).
