# combat.py

import pygame
import random
import time

class CombatScreen:
    def __init__(self, screen, change_scr, player_board, opponent_board):
        self.screen = screen
        self.change_scr = change_scr
        
        # فقط مینیون‌های واقعی (غیر None) رو نگه می‌داریم
        self.player_board = [m for m in player_board if m is not None]
        self.opponent_board = [m for m in opponent_board if m is not None]
        
        self.font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 36)
        self.damage_font = pygame.font.Font(None, 48)  # فونت جدا برای اعداد دمیج

        self.animation_timer = 0.0
        self.damage_numbers = []   # [(value, x, y, remaining_time, color)]
        self.shake_timer = 0.0
        self.shake_offset = (0, 0)

        self.attack_cooldown = 2.8  # هر چند ثانیه یک حمله
        self.last_attack = time.time()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.change_scr("recruit")
                    print("Returned to Recruit")

    def update(self, dt):
        now = time.time()
        
        # حمله خودکار
        if now - self.last_attack > self.attack_cooldown:
            if self.player_board and self.opponent_board:
                self._perform_attack()
                self.last_attack = now

        # لرزش
        if self.shake_timer > 0:
            self.shake_timer -= dt
            self.shake_offset = (random.randint(-10, 10), random.randint(-10, 10))
        else:
            self.shake_offset = (0, 0)

        # محو شدن اعداد دمیج
        new_list = []
        for dmg in self.damage_numbers:
            value, x, y, timer, color = dmg
            timer -= dt
            if timer > 0:
                new_list.append((value, x, y, timer, color))
        self.damage_numbers = new_list

    def _perform_attack(self):
        attacker = self.player_board[0]
        target = self.opponent_board[0]

        dmg_to_target = attacker.c_attack
        dmg_to_attacker = target.c_attack

        target.c_health -= dmg_to_target
        attacker.c_health -= dmg_to_attacker

        # اعداد دمیج (منفی = قرمز)
        self.damage_numbers.append((-dmg_to_target,   400, 320, 1.4, (255, 60, 60)))
        self.damage_numbers.append((-dmg_to_attacker, 800, 320, 1.4, (255, 60, 60)))

        self.shake_timer = 0.45

        # حذف مرده‌ها
        self.player_board = [m for m in self.player_board if m.c_health > 0]
        self.opponent_board = [m for m in self.opponent_board if m.c_health > 0]

    def render(self, surface):
        surface.fill((30, 0, 60))

        # عنوان
        title = self.font.render("Combat Phase", True, (255, 220, 100))
        surface.blit(title, (surface.get_width() // 2 - title.get_width() // 2, 40))

        # راهنما
        hint = self.small_font.render("Press SPACE to return to Recruit", True, (200, 200, 220))
        surface.blit(hint, (surface.get_width() // 2 - hint.get_width() // 2, surface.get_height() - 60))

        # بورد بازیکن (چپ)
        player_label = self.small_font.render("Your Board", True, (100, 255, 140))
        surface.blit(player_label, (120, 130))

        for i, minion in enumerate(self.player_board):
            rect = pygame.Rect(100 + i * 180, 180, 160, 220)
            rect = rect.move(self.shake_offset)
            minion.draw(surface, rect)

        # بورد حریف (راست)
        opp_label = self.small_font.render("Opponent Board", True, (255, 100, 100))
        surface.blit(opp_label, (surface.get_width() - 300, 130))

        for i, minion in enumerate(self.opponent_board):
            rect = pygame.Rect(surface.get_width() - 260 - i * 180, 180, 160, 220)
            rect = rect.move(self.shake_offset)
            minion.draw(surface, rect)

        # اعداد دمیج (محو شدن و بالا رفتن)
        for value, x, y, timer, color in self.damage_numbers:
            alpha = int(255 * (timer / 1.4))
            text = self.damage_font.render(str(value), True, color)
            text.set_alpha(alpha)
            offset_y = int((1.4 - timer) * -70)   # بالا رفتن
            surface.blit(text, (x - text.get_width() // 2, y + offset_y))

        # اگر هر دو بورد خالی شدند
        if not self.player_board and not self.opponent_board:
            end_text = self.font.render("Battle Ended", True, (180, 180, 255))
            surface.blit(end_text, (surface.get_width() // 2 - end_text.get_width() // 2, surface.get_height() // 2))