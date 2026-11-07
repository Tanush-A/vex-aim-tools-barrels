"""What the two live programs share. Not a program itself: simple_cli runs the subclasses.

    BarrelViewer.fsm   the per-frame answer: each frame, the detector's boxes for that frame (once a second)
    BarrelTracker.fsm  boxes that persist over frames: shown after 3 of the last 4 frames agree (5 frames a second)

Both hold the detector as it stands (barrels.worldmap_bridge.BarrelDetectorHook.default()), the view modes, and
the capture commands (barrels.capture). Commands at the C> prompt:

    tm boxes | tm seg | tm both   which picture to show (boxes: yellow = orange barrel, green = blue; seg: the tint)
    tm save                       write the current raw frame as snapshots/robot_snapN.png (like the camera viewer's s key)
    tm rec                        write every frame for ten seconds into snapshots/rec_<stamp>/ (+ frames.json)

snapshots/ is created under the folder simple_cli was started from (barrels/live/) and is gitignored; import the
keepers with tools/import_snaps.py --src barrels/live/snapshots (DATA.md).
"""
from aim_fsm import *
from barrels import capture, worldmap_bridge as wb


class BarrelLive(StateMachineProgram):
    def __init__(self):
        super().__init__(aruco=False, particle_filter=False, speech=False,
                         launch_cam_viewer=False, launch_worldmap_viewer=False)
        self.hook = wb.BarrelDetectorHook.default()   # frozen v1 model + the stripe detector + provisional camera
        self.capture = capture.FrameCapture()         # snapshots/ next to the .fsm files
        self.mode = "boxes"
        self.last_count = None
        self.last_frame = None                        # robot.frame_count of the frame last handed to the detector
        self.said_no_image = False

    def tag(self):
        return type(self).__name__

    def new_frame(self):
        """The camera image if it is a frame we have not processed yet, else None."""
        image = self.robot.camera_image
        if image is None:
            if not self.said_no_image:
                print(f"{self.tag()}: no camera image yet")
                self.said_no_image = True
            return None
        count = getattr(self.robot, "frame_count", None)
        if count is not None and count == self.last_frame:
            return None
        self.last_frame = count
        return image

    def report(self, barrels):
        """One console line when the number of barrels shown changes (not every frame)."""
        n = len(barrels)
        if n != self.last_count:
            names = ", ".join(b.color_name for b in barrels) or "none"
            print(f"{self.tag()}: {n} barrel{'s' if n != 1 else ''} ({names})")
            self.last_count = n
        line = self.capture.pop_report()
        if line:
            print(f"{self.tag()}: {line}")

    def user_image(self, image, gray):
        """aim_fsm calls this with every camera frame (on the image thread): only the recorder lives here."""
        try:
            self.capture.on_frame(image, getattr(self.robot, "frame_count", None))
        except Exception as e:                        # noqa: BLE001 — never let a disk error take the stream down
            print(f"{self.tag()}: recording stopped: {e}")
            self.capture.stop_recording()

    class SetMode(StateNode):
        def __init__(self, mode):
            super().__init__()
            self.mode = mode

        def start(self, event=None):
            super().start(event)
            self.parent.mode = self.mode
            print(f"{self.parent.tag()}: showing {self.mode}")

    class Save(StateNode):
        def start(self, event=None):
            super().start(event)
            image = self.robot.camera_image
            if image is None:
                print(f"{self.parent.tag()}: no camera image to save")
                return
            print(f"{self.parent.tag()}: saved {self.parent.capture.save(image)}")

    class Record(StateNode):
        def start(self, event=None):
            super().start(event)
            cap = self.parent.capture
            print(f"{self.parent.tag()}: recording {cap.rec_seconds:g} s into {cap.start_recording()}")
