# screens/recruit_screen.py

import pygame
import random
from src.button import Button
from src.minion import Minion
from src.minion_db import MINIONS_DB
from src.services.economy import Economy

class RecruitScreen:
    def __init__(self, screen, change_scr, hero_name):
        self.screen = screen
        self.change_scr = change_scr
        self.hero_name = hero_name

        self.economy = Economy()  # اقتصاد کامل
        self.health = 40

        self.shop = []
        self.hand = []
        self.board = []

        self.dragging = None
        self.drag_offset = (0, 0)

        self.info_font = pygame.font.Font(None, 32)

        # دکمه‌ها
        btn_y = screen.get_height() - 80
        self.end_turn_button = Button(
            x=screen.get_width() - 150, y=btn_y,
            width=120, height=50, text="End Turn", on_click=self.end_turn
        )
        self.refresh_button = Button(
            x=screen.get_width() - 280, y=btn_y,
            width=120, height=50, text="Refresh (1)", on_click=self.refresh_shop
        )
        self.upgrade_button = Button(
            x=screen.get_width() - 410, y=btn_y,
            width=120, height=50, text="Upgrade", on_click=self.upgrade_tavern
        )

        # اسلات‌ها
        self.shop_slots = self.create_slots(5, 100, 100, 100, 140, 20)
        self.board_slots = self.create_slots(7, 100, 350, 80, 110, 15)
        self.hand_slots = self.create_slots(10, 100, 500, 70, 95, 10)

        self.refresh_shop(initial=True)

    def create_slots(self, count, start_x, start_y, w, h, gap):
        return [pygame.Rect(start_x + i * (w + gap), start_y, w, h) for i in range(count)]

    def refresh_shop(self, initial=False):
        if not initial and not self.economy.spend(1):
            print("Not enough gold to refresh!")
            return
        available = [d for d in MINIONS_DB.values() if d["tier"] <= self.economy.tavern.tier]
        self.shop = [Minion(random.choice(available)) for _ in range(5)]
        print(f"Shop refreshed. Gold: {self.economy.gold}")

    def upgrade_tavern(self):
        if self.economy.upgrade_tavern():
            print(f"Tavern upgraded to Tier {self.economy.tavern.tier}! Gold: {self.economy.gold}")
        else:
            print("Not enough gold!")

    def end_turn(self):
        self.economy.start_turn()
        print(f"Turn {self.economy.turn} | Gold: {self.economy.gold} | Tier: {self.economy.tavern.tier}")

    def get_minion_at_pos(self, pos):
        for i, m in enumerate(self.hand):
            if self.hand_slots[i].collidepoint(pos): return "hand", i, m
        for i, m in enumerate(self.board):
            if self.board_slots[i].collidepoint(pos): return "board", i, m
        for i, m in enumerate(self.shop):
            if self.shop_slots[i].collidepoint(pos): return "shop", i, m
        return None, None, None

    def handle_events(self, events):
        for event in events:
            self.end_turn_button.handle_event(event)
            self.refresh_button.handle_event(event)
            self.upgrade_button.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                source, idx, minion = self.get_minion_at_pos(pos)

                if source == "shop" and minion:
                    if self.economy.spend(minion.cost) and len(self.hand) < 10:
                        self.hand.append(minion)
                        del self.shop[idx]
                        if len(self.shop) < 5:
                            available = [d for d in MINIONS_DB.values() if d["tier"] <= self.economy.tavern.tier]
                            if available:
                                self.shop.append(Minion(random.choice(available)))
                        print(f"Bought {minion.name}. Gold: {self.economy.gold}")
                    else:
                        print("Not enough gold or hand full!")

                elif source in ["hand", "board"] and minion:
                    rect = self.hand_slots[idx] if source == "hand" else self.board_slots[idx]
                    self.dragging = (source, idx, minion)
                    self.drag_offset = (rect.x - pos[0], rect.y - pos[1])

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.dragging:
                    pos = pygame.mouse.get_pos()
                    source, idx, minion = self.dragging
                    target, t_idx, _ = self.get_minion_at_pos(pos)
                    if target == "board" and len(self.board) < 7 and source == "hand":
                        self.board.append(minion)
                        del self.hand[idx]
                    self.dragging = None

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                pos = pygame.mouse.get_pos()
                source, idx, minion = self.get_minion_at_pos(pos)
                if source in ["hand", "board"] and minion:
                    if source == "hand": del self.hand[idx]
                    else: del self.board[idx]
                    self.economy.gain(1)
                    print(f"Sold {minion.name}. Gold: {self.economy.gold}")

    def update(self, dt):
        pass

    def render(self, surface):
        surface.fill((20, 25, 35))

        surface.blit(self.info_font.render(f"Hero: {self.hero_name}", True, (255, 255, 255)), (30, 20))
        surface.blit(self.info_font.render(f"Gold: {self.economy.gold}", True, (255, 215, 0)), (200, 20))
        surface.blit(self.info_font.render(f"Tier: {self.economy.tavern.tier}", True, (180, 150, 255)), (350, 20))
        surface.blit(self.info_font.render(f"Upgrade Cost: {self.economy.tavern.upgrade_cost()}", True, (255, 200, 100)), (480, 20))
        surface.blit(self.info_font.render(f"Health: {self.health}", True, (255, 100, 100)), (650, 20))

        for i, m in enumerate(self.shop): m.draw(surface, self.shop_slots[i])
        for i, m in enumerate(self.board): m.draw(surface, self.board_slots[i])
        for i, m in enumerate(self.hand): m.draw(surface, self.hand_slots[i])

        if self.dragging:
            _, _, m = self.dragging
            pos = pygame.mouse.get_pos()
            rect = pygame.Rect(0, 0, 100, 140)
            rect.center = (pos[0] + self.drag_offset[0], pos[1] + self.drag_offset[1])
            m.draw(surface, rect)

        self.upgrade_button.text = f"Upgrade ({self.economy.tavern.upgrade_cost()})"
        self.end_turn_button.draw(surface)
        self.refresh_button.draw(surface)
        self.upgrade_button.draw(surface)