import pygame

import settings
import colors
import text
import main

pygame.init()

FONT = pygame.font.Font("fonts/MotionPicture.ttf", 64)
FONT2 = pygame.font.Font("fonts/MotionPicture.ttf", 76)
FONT3 = pygame.font.SysFont("Impact", 80)


class Menu(object):

    def __init__(self):
        self.running = True
        centerx, height = settings.WIDTH // 2, settings.HEIGHT
        self.title = text.Text("PACMAN-ish", pos=(centerx, 1 * height // 9), color=colors.LIGHT_RED, font=FONT3)
        self.button = {
            'start': text.ClickableText("Start", pos=(centerx, 3 * height // 9), font=FONT, hovered_font=FONT2),
            'menu': text.ClickableText("Menu", pos=(centerx, 5 * height // 9), font=FONT, hovered_font=FONT2),
            'quit': text.ClickableText("Quit", pos=(centerx, 7 * height // 9), font=FONT, hovered_font=FONT2),
                       }
        self.buttons = pygame.sprite.Group(self.button.values())

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        button = self.button
        if button['start'].pressed:
            main.main()
        elif button['menu'].pressed:
            pass
        elif button['quit'].pressed:
            quit()

    def main(self):
        clock = settings.CLOCK
        fps = settings.FPS
        screen = settings.SCREEN
        while self.running:
            clock.tick(fps) / 1000

            self.handle_events()

            self.buttons.update()

            screen.fill(colors.BLACK)
            self.buttons.draw(screen)
            screen.blit(self.title.image, self.title.rect)

            pygame.display.update()


if __name__ == '__main__':
    Menu().main()
