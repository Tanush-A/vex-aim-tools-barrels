from barrels import io, tracker
from barrels.detect_types import Barrel


def orange(x0=100, y0=200, x1=180, y1=290, **kw):
    return Barrel(color=io.ORANGE, bbox=(x0, y0, x1, y1), **kw)


def blue(x0=100, y0=200, x1=180, y1=290, **kw):
    return Barrel(color=io.BLUE, bbox=(x0, y0, x1, y1), **kw)


def test_a_one_frame_blip_never_shows_and_is_forgotten():
    tr = tracker.Tracker()
    assert tr.update([orange()]) == []                      # seen once: not shown
    assert len(tr.tracks) == 1
    for _ in range(4):
        assert tr.update([]) == []
    assert tr.tracks == []                                  # forgotten after max_misses frames without it


def test_shown_after_three_of_four_kept_through_one_miss_hidden_after_two():
    tr = tracker.Tracker()
    assert tr.update([orange()]) == [] and tr.update([orange()]) == []
    shown = tr.update([orange()])                           # third frame in a row: shown
    assert len(shown) == 1 and shown[0].bbox == (100, 200, 180, 290) and shown[0].color == io.ORANGE
    assert shown[0].source == "track" and shown[0].confidence == 0.75
    assert len(tr.update([orange()])) == 1 and tr.visible()[0].confidence == 1.0
    assert len(tr.update([])) == 1                          # one miss: still 3 of the last 4
    assert tr.visible()[0].bbox == (100, 200, 180, 290)     # the box does not move while unseen
    assert tr.update([]) == []                              # two misses: 2 of 4, hidden but remembered
    assert len(tr.tracks) == 1
    assert len(tr.update([orange()])) == 0                  # seen again: hit, miss, miss, hit = 2 of 4
    assert len(tr.update([orange()])) == 0                  # miss, miss, hit, hit = 2 of 4
    assert len(tr.update([orange()])) == 1                  # miss, hit, hit, hit = 3 of 4: shown, same track (not a new one)
    assert len(tr.tracks) == 1


def test_a_moving_barrel_is_followed_and_one_odd_frame_does_not_move_the_box():
    tr = tracker.Tracker()
    for k in range(3):
        shown = tr.update([orange(100 + 10 * k, 200, 180 + 10 * k, 290)])
    assert len(shown) == 1 and shown[0].bbox == (110, 200, 190, 290)      # median of the last three
    shown = tr.update([orange(130, 200, 210, 340)])                        # one frame with the bottom 50 px off
    assert len(tr.tracks) == 1 and shown[0].bbox[3] == 290                 # median ignores it
    shown = tr.update([orange(140, 200, 220, 290)])
    assert shown[0].bbox == (130, 200, 210, 290)


def test_color_and_overlap_decide_who_continues_whom():
    tr = tracker.Tracker()
    for _ in range(3):
        tr.update([orange(), blue(300, 200, 380, 290)])
    assert [b.color for b in tr.visible()] == [io.ORANGE, io.BLUE]
    # a blue box where the orange one was starts a new track; the orange track misses
    shown = tr.update([blue(100, 200, 180, 290), blue(300, 200, 380, 290)])
    assert [b.color for b in shown] == [io.ORANGE, io.BLUE] and len(tr.tracks) == 3
    # two orange detections, listed in the other order, each continue their own track (best overlap first)
    tr2 = tracker.Tracker()
    for _ in range(3):
        tr2.update([orange(100, 200, 180, 290), orange(400, 200, 480, 290)])
    shown = tr2.update([orange(405, 200, 485, 290), orange(95, 200, 175, 290)])
    assert [b.bbox[0] for b in shown] == [100, 400] and len(tr2.tracks) == 2
    # a box far from any track starts a new track rather than stealing one
    shown = tr2.update([orange(100, 200, 180, 290), orange(400, 200, 480, 290), orange(250, 100, 330, 190)])
    assert len(tr2.tracks) == 3 and len(shown) == 2


def test_reset_forgets_everything():
    tr = tracker.Tracker()
    for _ in range(3):
        tr.update([orange()])
    assert tr.visible() and tr.frame == 3
    tr.reset()
    assert tr.tracks == [] and tr.visible() == [] and tr.frame == 0
