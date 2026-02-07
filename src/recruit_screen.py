import pygame
import random
import time
from button import Button
from minion import Minion
from minion_db import MINIONS_DB
from services.economy import Economy


class RecruitScreen:
    def __init__(self, screen, change_scr, hero_name):
        self.screen = screen
        self.change_scr = change_scr
        self.hero_name = hero_name

        self.economy = Economy()
        self.health = 40
        self.shop_frozen = False

        self.shop = []
        self.hand = []
        self.board = [None] * 7

        self.dragging = None

        # انیمیشن ساده fade-in
        self.fade_timers = {}  # (type, idx) -> remaining time

        self.info_font = pygame.font.Font(None, 34)
        self.log_font = pygame.font.Font(None, 20)
        self.card_font = pygame.font.Font(None, 28)

        self.log = []
        self.log_message(f"Game started | Hero: {hero_name}")

        # دکمه‌ها
        btn_y = screen.get_height() - 90
        bw, bh, gap = 160, 60, 45
        start_x = (screen.get_width() - (4 * bw + 3 * gap)) // 2

        self.freeze_button   = Button(start_x, btn_y, bw, bh, "Freeze",   self.toggle_freeze)
        self.refresh_button  = Button(start_x + bw + gap, btn_y, bw, bh, "Refresh (1)", self.refresh_shop)
        self.upgrade_button  = Button(start_x + 2*(bw + gap), btn_y, bw + 40, bh, "Upgrade", self.upgrade_tavern)
        self.end_turn_button = Button(start_x + 3*(bw + gap) + 40, btn_y, bw, bh, "End Turn", self.end_turn)

        # اسلات‌ها با فاصله مناسب
        self.shop_slots  = self._centered_slots(5, 100, 170, 240, 70)
        self.board_slots = self._centered_slots(7, 360, 170, 240, 70)
        self.hand_slots  = self._centered_slots(10, screen.get_height() - 280, 130, 190, 50)

        self.refresh_shop(initial=True)

    def _centered_slots(self, count, y, w, h, gap):
        total = count * w + (count - 1) * gap
        start = (self.screen.get_width() - total) // 2
        return [pygame.Rect(start + i*(w + gap), y, w, h) for i in range(count)]

    def log_message(self, msg):
        self.log.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
        if len(self.log) > 10:
            self.log.pop(0)

    def toggle_freeze(self):
        self.shop_frozen = not self.shop_frozen
        self.log_message(f"Shop {'FROZEN' if self.shop_frozen else 'UNFROZEN'}")

    def refresh_shop(self, initial=False):
        if not initial and not self.economy.spend(1):
            self.log_message("Not enough gold to refresh")
            return

        if not initial:
            self.log_message("Shop refreshed (-1 gold)")

        pool = [d for d in MINIONS_DB.values() if d["tier"] <= self.economy.tavern.tier]
        count = self.economy.tavern.get_shop_slots()
        self.shop = [Minion(random.choice(pool)) for _ in range(count)]

        # انیمیشن fade-in برای کارت‌های شاپ
        for i in range(len(self.shop)):
            self.fade_timers[("shop", i)] = 0.8  # 0.8 ثانیه fade

    def upgrade_tavern(self):
        cost = self.economy.tavern.upgrade_cost()
        if self.economy.upgrade_tavern():
            self.log_message(f"Tavern upgraded to Tier {self.economy.tavern.tier} (-{cost})")
            self.shop_slots = self._centered_slots(self.economy.tavern.get_shop_slots(), 100, 170, 240, 70)
            self.refresh_shop()
        else:
            self.log_message("Not enough gold to upgrade")

    def end_turn(self):
        self.economy.start_turn()
        if not self.shop_frozen:
            self.refresh_shop()
        else:
            self.shop_frozen = False
        self.log_message("Going to Combat!")
        self.change_scr("combat")

    def handle_events(self, events):
        for event in events:
            for btn in [self.freeze_button, self.refresh_button, self.upgrade_button, self.end_turn_button]:
                btn.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._start_drag(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.dragging:
                    self._handle_drop(pygame.mouse.get_pos())

    def _start_drag(self, pos):
        for src_type, cont, slots in [
            ("shop", self.shop, self.shop_slots),
            ("hand", self.hand, self.hand_slots),
            ("board", self.board, self.board_slots)
        ]:
            for i, r in enumerate(slots):
                if i < len(cont) and cont[i] and r.collidepoint(pos):
                    self.dragging = (cont[i], src_type, i, r.x - pos[0], r.y - pos[1])
                    return

    def _handle_drop(self, pos):
        if not self.dragging:
            return

        minion, src_type, src_idx, ox, oy = self.dragging
        self.dragging = None

        target_type, target_idx = None, None
        for t_type, cont, slots in [
            ("board", self.board, self.board_slots),
            ("hand", self.hand, self.hand_slots)
        ]:
            for i, r in enumerate(slots):
                if r.collidepoint(pos):
                    target_type = t_type
                    target_idx = i
                    break
            if target_type: break

        cost = minion.cost

        if src_type == "shop":
            if self.economy.gold < cost:
                self.log_message(f"Need {cost} gold")
                return
            self.shop.pop(src_idx)
            self.economy.spend(cost)
            if target_type == "board" and target_idx is not None and self.board[target_idx] is None:
                self.board[target_idx] = minion
                self.log_message(f"Played {minion.name} (-{cost}g)")
            else:
                self.hand.append(minion)
                self.log_message(f"Bought {minion.name} (-{cost}g)")

        elif src_type == "hand" and target_type == "board" and target_idx is not None and self.board[target_idx] is None:
            self.hand.pop(src_idx)
            self.board[target_idx] = minion
            self.log_message(f"Played {minion.name}")

        elif src_type == "board":
            if target_type is None:
                self.board[src_idx] = None
                self.economy.gain(1)
                self.log_message(f"Sold {minion.name} (+1g)")
            elif target_type == "hand" and len(self.hand) < 10:
                self.board[src_idx] = None
                self.hand.append(minion)
                self.log_message(f"Returned {minion.name}")

    def update(self, dt):
        # Fade-in کارت‌ها
        for key in list(self.fade_timers.keys()):
            self.fade_timers[key] -= dt
            if self.fade_timers[key] <= 0:
                del self.fade_timers[key]

    def render(self, surface):
        surface.fill((35, 5, 65))

        # هدر ثابت و مرتب
        self._text(surface, f"Hero: {self.hero_name}", 40, 25, (255, 255, 180))
        self._text(surface, f"Turn {self.economy.turn}", 40, 70, (200, 220, 255))
        self._text(surface, f"Gold: {self.economy.gold}", 200, 70, (255, 215, 0))
        self._text(surface, f"HP: {self.health}", surface.get_width() - 140, 25, (255, 90, 90))

        cost = self.economy.tavern.upgrade_cost()
        ccol = (100, 255, 100) if self.economy.gold >= cost else (255, 100, 100)
        self._text(surface, f"Tier {self.economy.tavern.tier} • Upgrade: {cost}g", surface.get_width()//2 - 200, 70, ccol)

        # اسلات‌ها (با قاب و فاصله مناسب)
        for slots, fill, border in [
            (self.shop_slots, (40, 40, 100, 120), (120, 140, 255)),
            (self.board_slots, (70, 30, 50, 120), (255, 120, 120)),
            (self.hand_slots, (30, 70, 30, 120), (100, 220, 100))
        ]:
            for r in slots:
                s = pygame.Surface(r.size, pygame.SRCALPHA)
                pygame.draw.rect(s, fill, (0,0,*r.size), border_radius=30)
                surface.blit(s, r.topleft)
                pygame.draw.rect(surface, border, r, 6, border_radius=30)

        # کارت‌ها + اسلات خالی
        for cont, slots, src_type in [
            (self.shop, self.shop_slots, "shop"),
            (self.board, self.board_slots, "board"),
            (self.hand, self.hand_slots, "hand")
        ]:
            for i, item in enumerate(cont):
                if i < len(slots):
                    r = slots[i]
                    if item:
                        alpha = int(255 * (self.fade_timers.get((src_type, i), 0.8) / 0.8)) if (src_type, i) in self.fade_timers else 255
                        card_surf = pygame.Surface((170, 240), pygame.SRCALPHA)
                        item.draw(card_surf, pygame.Rect(0, 0, 170, 240))
                        card_surf.set_alpha(alpha)
                        surface.blit(card_surf, r.topleft)
                    else:
                        pygame.draw.rect(surface, (70, 70, 80, 100), r, border_radius=30)
                        empty = self.card_font.render("Empty", True, (150, 150, 170))
                        surface.blit(empty, empty.get_rect(center=r.center))

        # درگ
        if self.dragging:
            m, _, _, ox, oy = self.dragging
            mx, my = pygame.mouse.get_pos()
            r = pygame.Rect(mx + ox, my + oy, 170, 240)
            s = pygame.Surface(r.size, pygame.SRCALPHA)
            s.set_alpha(220)
            m.draw(s, pygame.Rect(0, 0, 170, 240))
            surface.blit(s, r.topleft)

        # دکمه‌ها
        self.freeze_button.text = "Unfreeze" if self.shop_frozen else "Freeze"
        self.freeze_button.color = (200, 70, 70) if self.shop_frozen else (80, 140, 190)
        self.refresh_button.text = f"Refresh ({1 if self.economy.gold >=1 else '-'})"
        self.upgrade_button.text = f"Upgrade ({self.economy.tavern.upgrade_cost()})"

        for btn in [self.freeze_button, self.refresh_button, self.upgrade_button, self.end_turn_button]:
            btn.draw(surface)

        # لاگ (کوچک و مرتب)
        log_rect = pygame.Rect(surface.get_width() - 340, 110, 320, surface.get_height() - 220)
        pygame.draw.rect(surface, (25, 25, 45), log_rect, border_radius=20)
        pygame.draw.rect(surface, (100, 100, 170), log_rect, 5, border_radius=20)
        self._text(surface, "Game Log", log_rect.x + 20, log_rect.y + 20, (220, 220, 255))

        y = log_rect.y + 55
        for line in self.log:
            self._text(surface, line, log_rect.x + 20, y, (210, 230, 255), self.log_font)
            y += 26

    def _text(self, surf, txt, x, y, color, font=None):
        f = font or self.info_font
        t = f.render(txt, True, color)
        surf.blit(t, (x, y))