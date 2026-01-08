
class Board:
    def __init__(self):
        self.slots = [None] * 7 

    def place(self, index, minion):
        if 0 <= index < len(self.slots) and self.slots[index] is None:
            self.slots[index] = minion
            return True
        return False

    def remove(self, index):
        if 0 <= index < len(self.slots) and self.slots[index] is not None:
            minion = self.slots[index]
            self.slots[index] = None
            return minion
        return None

    def is_free(self, index):
        return 0 <= index < len(self.slots) and self.slots[index] is None

    def is_occupied(self, index):
        return 0 <= index < len(self.slots) and self.slots[index] is not None
    
    def snapshot_board(self) -> "Board":
        from src.services.minion_factory import clone_minion_state
        snap = Board()
        snap.slots = [(clone_minion_state(m, keep_instance_id = True) if m is not None else None) for m in self.slots]
        return snap