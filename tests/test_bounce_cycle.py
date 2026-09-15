"""BounceCycle decides when the avatar may change clips, so its cycle count
has to be exact — an off-by-one shows up as a visible cut mid-motion.

It lives in its own module so this runs without a display; see cycle.py."""

import pytest

from speak2me.cycle import BounceCycle


def test_ping_pong_order_without_repeating_the_endpoints():
    cycle = BounceCycle([1, 2, 3])
    assert [next(cycle) for _ in range(7)] == [1, 2, 3, 2, 1, 2, 3]


def test_one_cycle_is_a_full_round_trip():
    cycle = BounceCycle([1, 2, 3])
    for _ in range(3):  # 1, 2, 3 -> still on the way out
        next(cycle)
    assert cycle.cycles == 0
    next(cycle)  # yields 2 and lands back on the first frame
    assert cycle.cycles == 1
    assert next(cycle) == 1


def test_restart_resets_position_and_count():
    cycle = BounceCycle([1, 2, 3])
    for _ in range(5):
        next(cycle)
    cycle.restart()
    assert cycle.cycles == 0
    assert next(cycle) == 1


def test_two_frames_is_the_minimum():
    with pytest.raises(ValueError):
        BounceCycle([1])
