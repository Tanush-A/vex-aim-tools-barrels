import numpy as np

from barrels import io, viz


def test_render_outputs_colors():
    m = np.array([[io.OTHER, io.ORANGE], [io.BLUE, io.IGNORE]], np.uint8)
    o, b = viz.render_outputs(m)
    assert tuple(o[0, 1]) == (0, 128, 255) and tuple(o[0, 0]) == (128, 128, 128) and tuple(o[1, 0]) == (128, 128, 128)
    assert tuple(b[1, 0]) == (255, 100, 0) and tuple(b[0, 1]) == (128, 128, 128)
    assert tuple(o[1, 1]) == (128, 128, 128)


def test_debug_sheet_shape():
    img = np.zeros((4, 5, 3), np.uint8)
    m = np.zeros((4, 5), np.uint8)
    assert viz.debug_sheet(img, m, m).shape == (4, 15, 3)
    assert viz.debug_sheet(img, m).shape == (4, 10, 3)
