import pygame
import sys
import colors
pygame.init()


class Text(pygame.sprite.Sprite):

    def __init__(self, text: str, pos=(0, 0), origin='center', color=colors.GREY, font=pygame.font.SysFont(None, 32)):
        """
        Creates a static text surface.

        :param text: The text to display.
        :param pos: It's position on the screen.
        :param origin: What part of the rect to place on the given position.GREY
        :param color: The color of the text (when hovered over it'll add 50 for each of R, G and B, making it brighter).
        :param font: The font of the text.
        :type text: str or int or float
        :type pos: 2 element iterable
        :type origin: str
        :type color: 3 or 4 element iterable
        :type font: pygame.font.Font or pygame.font.SysFont
        """
        super(Text, self).__init__()
        self.text = str(text)
        self.color = pygame.Color(*color) if not isinstance(color, pygame.Color) else color
        self.font = font
        self.image = font.render(self.text, True, self.color)
        self.rect = self.image.get_rect()
        setattr(self.rect, origin, pos)


class ClickableText(Text):
    """
    A clickable text for pygame. Is a subclass of pygame.sprite.Sprite class and can be used with pygame.sprite.Group or
    other sprite group classes.
    """
    def __init__(self, text: str, hovered_font=pygame.font.SysFont(None, 32), **kwargs):
        """
        Creates text which highlights when hovered over and keeps track if it's pressed or not.

        :param text: The text to display.
        :param font: The font of the text.
        :type text: str
        :type font: pygame.font.Font or pygame.font.SysFont
        """
        super(ClickableText, self).__init__(text, **kwargs)
        if hovered_font is None:
            font = pygame.font.SysFont(None, int(self.font.get_height() * 1.2))  # Check how to get the size.
            self.hovered_image = font.render(self.text, 1, self.color + colors.GREY)
        else:
            self.hovered_image = hovered_font.render(self.text, 1, self.color + colors.GREY)

        self.delta_color = colors.DARK_GREY
        self.pressed = False
        self.hover = False

        self.images = (self.image, self.hovered_image)
        self.rects = (self.rect, self.images[1].get_rect(center=self.rect.center))

    def update(self, *ignore):
        """Should be called every game loop to check if the user is hovering or clicking the text."""
        if self.pressed:  # Making sure 'self.pressed' is reset every game loop.
            self.pressed = False
        if self.rect.collidepoint(*pygame.mouse.get_pos()):
            self.image = self.images[1]
            self.rect = self.rects[1]
            if not self.hover:
                self.hover = True
            if pygame.mouse.get_pressed()[0]:
                self.pressed = True
        else:
            self.image = self.images[0]
            self.rect = self.rects[0]
            if self.hover:
                self.hover = False


class FadingText(Text):
    """
    A fading text for pygame. Is a subclass of pygame.sprite.Sprite class and can be used with pygame.sprite.Group or
    other sprite group classes.
    """

    def __init__(self, text, fade_in=0, stay=1, fade_out=0, **kwargs):
        """
        Creates a text that fades in and out. Will dereferenced itself from pygame sprite groups when done but needs to
        be manually dereferenced if referenced outside a sprite group. It's ready to be dereferenced when
        'self.dead = True'

        :param text: The text to display.
        :param fade_in: Time to fade in to full opaque, in seconds.
        :param stay: Time to display the text in opaque, in seconds.
        :param fade_out: Time to fade out to full transparency, in seconds.
        :param kwargs:
        """
        super(FadingText, self).__init__(text, **kwargs)
        self.fade_in = [fade_in, fade_in]
        self.stay = stay
        self.fade_out = [fade_out, fade_out]
        self.dead = False
        _ = pygame.Surface(self.image.get_size())
        _.set_colorkey(colors.BLACK)
        _.blit(self.image, (0, 0))
        _.set_alpha(0) if fade_in > 0 else 255
        self.image = _

    def update(self, dt, *ignore):
        """Needs to be passed the delta time. Will ignore all other value passed than the first."""
        if self.dead:
            return

        fade_in = self.fade_in
        fade_out = self.fade_out

        if fade_in[0] > 0:
            alpha = 255 - (fade_in[0] / fade_in[1]) * 255  # 255 being fully opaque.
            self.image.set_alpha(alpha)
            self.fade_in[0] -= dt
        elif self.stay > 0:
            self.stay -= dt
        elif fade_out[0] > 0:
            alpha = (fade_out[0] / fade_out[1]) * 255  # 255 being fully opaque.
            self.image.set_alpha(alpha)
            self.fade_out[0] -= dt
        else:
            self.kill()
            self.image.set_alpha(0)
            self.dead = True


def put_fit_text(surface, text, color=colors.WHITE, max_size=128, font_name='Arial', origin='center'):
    """
    Put text that fits inside given surface. Text will have a font size of 'max_size' or less.

    :param surface: The surface to put text onto.
    :param text: The text to put on the surface.
    :param color: A 3 or 4 element sequence of R, G, B (and A, but alpha will have no effect).
    :param max_size: The maximum size of the text.
    :param font_name: The font for the text.
    :param origin: What part of the rect to place on the given position.
    :type surface: pygame.Surface
    :type text: str
    :type color: tuple, list, pygame.Color
    :type max_size: int
    :type font_name: str
    :type origin: str
    :return: None. Works directly on the Surface.
    """
    surface_width, surface_height = surface.get_size()
    lower, upper = 0, max_size
    while True:
        font = pygame.font.SysFont(font_name, max_size)
        font_width, font_height = font.size(text)

        if upper - lower <= 1:
            break
        elif max_size < 1:
            print("Text can't fit in the given surface.", file=sys.stderr)
            raise ValueError
        elif font_width > surface_width or font_height > surface_height:
            upper = max_size
            max_size = (lower + upper) // 2
        elif font_width < surface_width or font_height < surface_height:
            lower = max_size
            max_size = (lower + upper) // 2
        else:
            break
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    setattr(text_rect, origin, getattr(surface.get_rect(), origin))
    surface.blit(text_surface, text_rect)


def put_text(surface, text, pos, color=colors.WHITE, font=pygame.font.SysFont(None, 32), origin='center'):
    x = pos[0] if pos[0] >= 0 else surface.get_width() + pos[0]
    y = pos[1] if pos[1] >= 0 else surface.get_height() + pos[1]
    text_surface = font.render(text, 1, color)
    rect = text_surface.get_rect()
    setattr(rect, origin, (x, y))
    surface.blit(text_surface, rect)
    return rect
