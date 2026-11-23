import json

import pytest

from barrels import conditions as cd


def test_the_committed_table_loads_and_covers_today():
    t = cd.load_table()
    for key in ("window_light", "campus_light", "lampwarm6_ottoman", "both_abpgray", "overheaddim_palewood"):
        assert key in t
    assert cd.info("lampwarm6_ottoman").place == cd.info("lampmid3_ottoman").place     # one place, four lights
    assert cd.info("both_abpgray").light == "mixed"
    assert not cd.info("window_light").guessed


def test_a_missing_condition_is_guessed_and_flagged():
    i = cd.info("lampwarm6_glass", table={})
    assert (i.place, i.light, i.guessed) == ("glass", "lamp", True)
    assert cd.info("both_glass", table={}).light == "mixed"
    assert cd.info("mixlamp_glass", table={}).light == "mixed"
    assert cd.info("overhead_bathtile", table={}).light == "overhead"
    assert cd.info("sunset_x", table={}).light == cd.UNKNOWN


def test_a_bad_entry_is_refused(tmp_path):
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"version": 1, "conditions": {"window_glass": {"place": "g", "light": "sun"}}}))
    with pytest.raises(ValueError):
        cd.load_table(p)
    p.write_text(json.dumps({"version": 1, "conditions": {"window_glass": {"place": "g", "light": "window"}}}))
    assert cd.info("window_glass", cd.load_table(p)).place == "g"
    assert cd.load_table(tmp_path / "missing.json") == {}
