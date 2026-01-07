import pygame

class DragManager:
    def __init__(self, event_bus=None):
        self.event_bus = event_bus
        self.dragging = None
        self.valid_drop_zone = None 

    def start_drag(self, minion, zone, index, mouse_pos, minion_rect):
        offset_x = minion_rect.x - mouse_pos[0]
        offset_y = minion_rect.y - mouse_pos[1]
        self.dragging = (minion, zone, index, offset_x, offset_y)
        self.valid_drop_zone = None

    def update(self, mouse_pos, board_slots):
        if not self.dragging:
            return

        self.valid_drop_zone = None
        for i, slot_rect in enumerate(board_slots):
            if len(board_slots) > i and slot_rect.collidepoint(mouse_pos):
                self.valid_drop_zone = ("board", i)
                break

    def end_drag(self):
        if not self.dragging:
            return

        minion, source_zone, source_index, _, _ = self.dragging

        action = None
        if self.valid_drop_zone and self.valid_drop_zone[0] == "board":
            if source_zone == "hand":
                action = {
                    "action": "PLAY",
                    "source_hand_slot": source_index,
                    "target_board_slot": self.valid_drop_zone[1]
                }
            elif source_zone == "shop":
                action = {
                    "action": "BUY_AND_PLAY",
                    "shop_slot": source_index,
                    "target_board_slot": self.valid_drop_zone[1]
                }
        elif source_zone == "shop":
            action = {
                "action": "BUY",
                "shop_slot": source_index
            }

        if action and self.event_bus:
            self.event_bus.post_server(action)
        elif action:
            print("[DRAG ACTION]", action) 

        self.dragging = None
        self.valid_drop_zone = None

    def draw(self, surface, mouse_pos):
        if self.dragging:
            minion, _, _, offset_x, offset_y = self.dragging
            draw_x = mouse_pos[0] + offset_x
            draw_y = mouse_pos[1] + offset_y
            temp_rect = pygame.Rect(draw_x, draw_y, 100, 140)
            overlay = pygame.Surface((100, 140), pygame.SRCALPHA)
            overlay.set_alpha(200)
            minion.draw(overlay, temp_rect)
            surface.blit(overlay, (draw_x, draw_y))

    def get_highlight_slot(self):
        if self.valid_drop_zone and self.valid_drop_zone[0] == "board":
            return self.valid_drop_zone[1]
        return None