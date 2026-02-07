import pygame
import random
from title_screen import Title
from hero_select import HeroSelect
from recruit_screen import RecruitScreen
from combat import CombatScreen
from minion import Minion
from minion_db import MINIONS_DB

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 700))
        pygame.display.set_caption("Hearthstone Battlegrounds")
        self.clock = pygame.time.Clock()
        self.running = True

        self.screens = {}
        self.current_screen = None

        self.screens["title"] = Title(self.screen, self.change_screen)
        self.screens["hero_select"] = HeroSelect(self.screen, self.change_screen)
        self.screens["recruit"] = None
        self.screens["combat"] = None

        self.change_screen("title")

    def change_screen(self, name, **kwargs):
        if name == "recruit" and "hero" in kwargs:
            self.screens["recruit"] = RecruitScreen(self.screen, self.change_screen, kwargs["hero"])
        elif name == "combat":
            player_board = self.screens["recruit"].board[:] if self.screens["recruit"] else []
            opponent = [Minion(random.choice(list(MINIONS_DB.values()))) for _ in range(random.randint(2, 5))]  # اصلاح minion به Minion
            self.screens["combat"] = CombatScreen(self.screen, self.change_screen, player_board, opponent)
        self.current_screen = self.screens.get(name)

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            if self.current_screen:
                self.current_screen.handle_events(events)
                self.current_screen.update(dt)
                self.current_screen.render(self.screen)

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    Game().run()