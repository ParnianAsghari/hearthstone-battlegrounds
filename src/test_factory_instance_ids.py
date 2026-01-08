from src.services.minion_factory import create_minion_by_id, reset_instance_counter
import pygame

print("TEST_FACTORY FILE LOADED")
def run():
    pygame.init()
    pygame.font.init()

    from src.services.minion_factory import create_minion_by_id, reset_instance_counter
    from src.minion_db import MINIONS_DB

    reset_instance_counter(1)

    minion_id = next(iter(MINIONS_DB.keys()))
    m1 = create_minion_by_id(minion_id)
    m2 = create_minion_by_id(minion_id)
    m3 = create_minion_by_id(minion_id)

    print(m1.instance_id, m2.instance_id, m3.instance_id)

    assert m1.instance_id != m2.instance_id
    assert m2.instance_id != m3.instance_id
    assert m1.instance_id != m3.instance_id

    print("FACTORY instance_id TEST PASSED")

if __name__ == "__main__":
    run()
