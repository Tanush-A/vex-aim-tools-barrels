"""What the two live programs share. Not a program itself: simple_cli runs the subclasses.

    BarrelViewer.fsm   the per-frame answer: each frame, the detector's boxes for that frame (once a second)
    BarrelTracker.fsm  boxes that persist over frames: shown after 3 of the last 4 frames agree (5 frames a second)

Both hold the detector as it stands (barrels.worldmap_bridge.BarrelDetectorHook.default()), the view modes, and
the capture commands (barrels.capture). Commands at the C> prompt:

    tm boxes | tm seg | tm both   which picture to show. boxes: yellow = orange barrel, green = blue. seg: the main
                                  window dims every pixel not classified as a barrel color, and a second window
                                  ("<title> seg") shows only the classified pixels, in their class color on black.
                                  both: seg with the boxes on the main window. Back to boxes closes the second window.
    tm save                       write the current raw frame as snapshots/robot_snapN.png (like the camera viewer's s key),
                                  plus robot_snapN_vendor.json (what the robot's built-in detector reported when that
                                  frame arrived) and robot_snapN_vendor.png (a copy with the vendor's boxes, to look at)
    tm rec                        write every frame for ten seconds into snapshots/rec_<stamp>/ (+ frames.json, which
                                  also holds the vendor's answer per frame)

snapshots/ is created under the folder simple_cli was started from (barrels/live/) and is gitignored; import the
keepers with tools/import_snaps.py --src barrels/live/snapshots (DATA.md).
"""
from aim_fsm import *
from barrels import capture, worldmap_bridge as wb


class BarrelLive(StateMachineProgram):
    def __init__(self):
        super().__init__(aruco=False, particle_filter=False, speech=False,
                         launch_cam_viewer=False, launch_worldmap_viewer=False)
        self.hook = wb.BarrelDetectorHook.default()   # pipeline.detect_frame: hs colors + the detector + the stripe by contrast
        self.capture = capture.FrameCapture()         # snapshots/ next to the .fsm files
        self.mode = "boxes"
        self.last_count = None
        self.last_frame = None                        # robot.frame_count of the frame last handed to the detector
        self.said_no_image = False
        self.seg_window = None                        # title of the second (segmented-only) window while it is open
        self.latest = None                            # (image, frame count, vendor grab) of the newest camera frame (set by user_image)

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

    def show(self, title, picture):
        """Show the main picture, and keep the second window in step with the mode: in seg / both it shows only the
        segmented pixels (hook.seg_only()); in boxes it is closed. Called from ShowFrame, like the imshow it replaces
        (Dave's imshow / destroyWindow queue the window work for the main thread themselves)."""
        imshow(title, picture)
        seg = self.hook.seg_only() if self.mode in wb.SEG_VIEWS else None
        if seg is not None:
            self.seg_window = f"{title} seg"
            imshow(self.seg_window, seg)
        elif self.seg_window is not None:
            destroyWindow(self.seg_window)
            self.seg_window = None

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
        """aim_fsm calls this with every camera frame (on the image thread). It notes what the vendor detector says
        at that moment (a reference into the robot's status: no copy, no request to the robot), so `tm save` can
        store a frame and the vendor's answer for the same instant; and it feeds the recorder."""
        count, grab = None, None
        try:
            count = getattr(self.robot, "frame_count", None)
            grab = capture.grab_vendor(self.robot)    # never raises
            self.latest = (image, count, grab)
        except Exception:                             # noqa: BLE001 — never let this take the stream down
            pass
        try:
            self.capture.on_frame(image, count, vendor=grab)
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
            program, cap, record = self.parent, self.parent.capture, None
            latest = program.latest
            if latest is not None:                    # the newest frame, with the vendor's answer noted as it arrived
                image, count, grab = latest
                read_at = "frame"
            else:                                     # no frame has come through user_image yet: read both now
                image, count, grab, read_at = self.robot.camera_image, getattr(self.robot, "frame_count", None), None, "save"
            if image is None:
                print(f"{program.tag()}: no camera image to save")
                return
            try:
                if grab is None:
                    grab = capture.grab_vendor(self.robot)
                record = capture.vendor_record(grab, (image.shape[1], image.shape[0]), count, read_at)
            except Exception as e:                    # noqa: BLE001 — the frame is saved whatever happens to the vendor data
                print(f"{program.tag()}: vendor data skipped: {e}")
            path = cap.save(image, vendor=record)
            line = f"saved {path}"
            if record is not None:
                line += f" | {capture.vendor_summary(record)}"
                if cap.vendor_error:
                    line += f" | vendor files NOT written: {cap.vendor_error}"
            print(f"{program.tag()}: {line}")

    class Record(StateNode):
        def start(self, event=None):
            super().start(event)
            cap = self.parent.capture
            print(f"{self.parent.tag()}: recording {cap.rec_seconds:g} s into {cap.start_recording()}")
