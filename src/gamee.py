import pygame
from src.title_screen import Title
from src.hero_select import HeroSelect
from src.recruit_screen import RecruitScreen

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((900, 600))
        pygame.display.set_caption("Hearthstone Battlegrounds")
        self.clock = pygame.time.Clock()
        self.running = True

        self.screens = {}
        self.current_screen = None

        self.screens["title"] = Title(self.screen, self.change_screen)
        self.screens["hero_select"] = HeroSelect(self.screen, self.change_screen)

        self.change_screen("title")

    def change_screen(self, name, **kwargs):
        if name == "recruit" and "hero" in kwargs:
            self.screens["recruit"] = RecruitScreen(self.screen, self.change_screen, kwargs["hero"])
        self.current_screen = self.screens.get(name)

    def run(self):
        while self.running:
            dt = self.clock.tick(60)
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