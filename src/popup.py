# popup.py

import pygame

class DiscoverPopup:
    def __init__(self, screen, options, callback):
        self.screen = screen
        self.options = options  # لیست 3 تا Minion
        self.callback = callback  # تابعی که وقتی انتخاب شد صدا زده بشه
        self.active = True
        self.rects = []

    def handle_events(self, events):
        if not self.active:
            return
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(self.rects):
                    if rect.collidepoint(event.pos):
                        self.callback(self.options[i])
                        self.active = False
                        return

    def render(self, surface):
        if not self.active:
            return

        # پس‌زمینه نیمه‌شفاف
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # عنوان
        font = pygame.font.Font(None, 60)
        title = font.render("Discover a Minion", True, (255, 255, 200))
        surface.blit(title, (surface.get_width() // 2 - title.get_width() // 2, 150))

        # رسم ۳ گزینه
        self.rects = []
        for i, minion in enumerate(self.options):
            rect = pygame.Rect(surface.get_width() // 2 - 240 + i * 160, 250, 150, 210)
            # قاب طلایی
            pygame.draw.rect(surface, (255, 215, 0), rect, 8, border_radius=20)
            minion.draw(surface, rect.inflate(-20, -20))
            self.rects.append(rect)