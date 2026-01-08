import pygame

from src.minion import Minion

def make_minion(hp: int, ds: bool):
    data = {
        "id": "t1",
        "name": "TestMinion",
        "tier": 1,
        "base_attack": 3,
        "base_health": hp,
        "tribe": "none",
        "abilities": (["divine_shield"] if ds else []),
    }
    m = Minion(data)
    m.zone = "board"
    m.on_board = True
    m.board_position = 0
    return m

def run():
    pygame.init()
    pygame.font.init()

    # سناریو 1: بدون DS، ضربه کشنده
    m1 = make_minion(hp=2, ds=False)
    out1 = m1.damage_khor(2)
    assert out1 == "Killed!"
    assert m1.alive is False
    assert m1.zone == "grave"
    assert m1.board_position is None

    # سناریو 2: با DS، ضربه اول فقط DS را می‌شکند و HP کم نمی‌شود
    m2 = make_minion(hp=5, ds=True)
    out2 = m2.damage_khor(3)
    assert out2 == "Divine_shield broken"
    assert m2.divine_shield is False
    assert m2.c_health == 5
    assert m2.alive is True
    assert m2.zone == "board"
    assert m2.board_position == 0

    # سناریو 3: با DS، ضربه اول DS را می‌شکند، ضربه دوم می‌کُشد
    m3 = make_minion(hp=2, ds=True)
    out3a = m3.damage_khor(999)
    assert out3a == "Divine_shield broken"
    assert m3.c_health == 2
    assert m3.alive is True

    out3b = m3.damage_khor(2)
    assert out3b == "Killed!"
    assert m3.alive is False
    assert m3.zone == "grave"
    assert m3.board_position is None

    print("ALL TESTS PASSED ✅")

if __name__ == "__main__":
    run()
