import pygame
import random
import math 
from src.button import Button
from src.minion import Minion
from src.minion_db import MINIONS_DB
from src.services.economy import Economy

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
        self.board = []

        self.dragging = None
        self.drag_offset = (0, 0)

        self.info_font = pygame.font.Font(None, 32)
        self.big_font = pygame.font.Font(None, 48)

        self.gold_full_timer = 0.0
        self.gold_shake_offset = (0, 0)

        btn_y = screen.get_height() - 90
        self.end_turn_button = Button(
            x=screen.get_width() - 170, y=btn_y,
            width=140, height=60, text="End Turn", on_click=self.end_turn
        )
        self.refresh_button = Button(
            x=screen.get_width() - 350, y=btn_y,
            width=140, height=60, text="Refresh (1)", on_click=self.refresh_shop
        )
        self.upgrade_button = Button(
            x=screen.get_width() - 530, y=btn_y,
            width=160, height=60, text="Upgrade", on_click=self.upgrade_tavern
        )
        self.freeze_button = Button(
            x=screen.get_width() - 710, y=btn_y,
            width=140, height=60, text="Freeze", on_click=self.toggle_freeze
        )

        current_slots = self.economy.tavern.get_shop_slots()
        self.shop_slots = self.create_slots(current_slots, 120, 100, 140, 200, 30)
        self.hand_slots = self.create_slots(10, 80, 520, 100, 140, 15)
        self.board_slots = self.create_slots(7, 180, 300, 120, 170, 25)

        self.refresh_shop(initial=True)

    def create_slots(self, count, start_x, start_y, w, h, gap):
        return [pygame.Rect(start_x + i * (w + gap), start_y, w, h) for i in range(count)]

    def toggle_freeze(self):
        self.shop_frozen = not self.shop_frozen
        status = "FROZEN" if self.shop_frozen else "UNFROZEN"
        print(f"Shop is now {status}")

    def refresh_shop(self, initial=False):
        if not initial and not self.economy.spend(1):
            print("Not enough gold to refresh!")
            return

        available = [d for d in MINIONS_DB.values() if d["tier"] <= self.economy.tavern.tier]
        if not available:
            return

        slots_count = self.economy.tavern.get_shop_slots()

        if self.shop_frozen and not initial and len(self.shop) == slots_count:
            print("Shop is frozen _ no refresh!")
            return

        self.shop = [Minion(random.choice(available)) for _ in range(slots_count)]
        print(f"Shop refreshed ({slots_count} slots). Gold left: {self.economy.gold}")

    def upgrade_tavern(self):
        cost = self.economy.tavern.upgrade_cost()
        if not self.economy.can_spend(cost):
            print(f"Not enough gold to upgrade! Need {cost}, have {self.economy.gold}")
            return

        if self.economy.upgrade_tavern():
            print(f"Tavern upgraded to Tier {self.economy.tavern.tier} for {cost} gold!")

            new_slots_count = self.economy.tavern.get_shop_slots()
            self.shop_slots = self.create_slots(new_slots_count, 120, 100, 140, 200, 30)

            if len(self.shop) < new_slots_count and not self.shop_frozen:
                self.refresh_shop()

    def end_turn(self):
        if not self.shop_frozen:
            self.refresh_shop()

        self.shop_frozen = False

        self.economy.start_turn()

        if self.economy.gold == 10:
            self.gold_full_timer = 2.0

        print(f"Turn {self.economy.turn} started | Gold: {self.economy.gold} | Tier: {self.economy.tavern.tier}")

    def get_minion_at_pos(self, pos):
        for i, m in enumerate(self.hand):
            if i < len(self.hand_slots) and self.hand_slots[i].collidepoint(pos):
                return "hand", i, m
        for i, m in enumerate(self.board):
            if i < len(self.board_slots) and self.board_slots[i].collidepoint(pos):
                return "board", i, m
        for i, m in enumerate(self.shop):
            if i < len(self.shop_slots) and self.shop_slots[i].collidepoint(pos):
                return "shop", i, m
        return None, None, None

    def handle_events(self, events):
        for event in events:
            self.end_turn_button.handle_event(event)
            self.refresh_button.handle_event(event)
            self.upgrade_button.handle_event(event)
            self.freeze_button.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                source, idx, minion = self.get_minion_at_pos(pos)

                if source == "shop" and minion:
                    if len(self.hand) >= 10:
                        print("Hand is full!")
                    elif not self.economy.can_spend(minion.cost):
                        print(f"Not enough gold! Need {minion.cost}")
                    else:
                        self.economy.spend(minion.cost)
                        self.hand.append(minion)
                        del self.shop[idx]
                        available = [d for d in MINIONS_DB.values() if d["tier"] <= self.economy.tavern.tier]
                        if available and len(self.shop) < len(self.shop_slots):
                            self.shop.append(Minion(random.choice(available)))
                        print(f"Bought {minion.name}. Gold: {self.economy.gold}")

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
                        print(f"Played {minion.name} to board")
                    elif target == "board":
                        print("Board is full!")

                    self.dragging = None

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                pos = pygame.mouse.get_pos()
                source, idx, minion = self.get_minion_at_pos(pos)
                if source in ["hand", "board"] and minion:
                    if source == "hand":
                        del self.hand[idx]
                    else:
                        del self.board[idx]
                    self.economy.gain(1)
                    print(f"Sold {minion.name} - +1 gold! Total: {self.economy.gold}")

    def update(self, dt):
        if self.gold_full_timer > 0:
            self.gold_full_timer -= dt
            intensity = 4
            freq = 15
            self.gold_shake_offset = (
                intensity * math.sin(self.gold_full_timer * freq),
                intensity * math.sin(self.gold_full_timer * freq + 1)
            )
        else:
            self.gold_shake_offset = (0, 0)

    def render(self, surface):
        surface.fill((20, 25, 35))

        gold_x = 200 + self.gold_shake_offset[0]
        gold_y = 20 + self.gold_shake_offset[1]
        gold_color = (255, 215, 0)
        if self.gold_full_timer > 0:
            flash = int(128 + 127 * math.sin(self.gold_full_timer * 20))
            gold_color = (255, 100 + flash // 2, 0)

        surface.blit(self.info_font.render(f"Hero: {self.hero_name}", True, (255, 255, 255)), (30, 20))
        surface.blit(self.big_font.render(f"{self.economy.gold}", True, gold_color), (gold_x, gold_y))
        surface.blit(self.info_font.render("/10", True, (180, 180, 180)), (gold_x + 60, gold_y + 10))
        surface.blit(self.info_font.render(f"Tavern Tier: * {self.economy.tavern.tier}", True, (180, 150, 255)), (350, 20))

        cost = self.economy.tavern.upgrade_cost()
        cost_color = (100, 255, 100) if self.economy.gold >= cost else (255, 100, 100)
        surface.blit(self.info_font.render(f"Upgrade: {cost} gold", True, cost_color), (520, 20))
        surface.blit(self.info_font.render(f"HP: {self.health}", True, (255, 100, 100)), (720, 20))

        # minion
        for i, m in enumerate(self.shop):
            if i < len(self.shop_slots):
                m.draw(surface, self.shop_slots[i])
        for i, m in enumerate(self.board):
            if i < len(self.board_slots):
                m.draw(surface, self.board_slots[i])
        for i, m in enumerate(self.hand):
            if i < len(self.hand_slots):
                m.draw(surface, self.hand_slots[i])

        # drag
        if self.dragging:
            _, _, m = self.dragging
            pos = pygame.mouse.get_pos()
            drag_rect = pygame.Rect(0, 0, 140, 200)
            drag_rect.center = (pos[0] + self.drag_offset[0], pos[1] + self.drag_offset[1])
            m.draw(surface, drag_rect)

        # buttons
        self.upgrade_button.text = f"Upgrade ({self.economy.tavern.upgrade_cost()})"
        self.freeze_button.text = "Unfreeze" if self.shop_frozen else "Freeze"
        self.freeze_button.color = (200, 80, 80) if self.shop_frozen else (70, 130, 180)

        self.end_turn_button.draw(surface)
        self.refresh_button.draw(surface)
        self.upgrade_button.draw(surface)
        self.freeze_button.draw(surface)