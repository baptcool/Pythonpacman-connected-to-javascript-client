import pygame
import os
pygame.init()


def load_sounds():
    sounds = {}
    sound_directory = os.path.join(os.getcwd(), 'sounds')
    for directory in os.listdir(sound_directory):
        if directory.startswith('.'):
            continue
        files = os.path.join(sound_directory, directory)
        sounds[directory] = {
            os.path.splitext(name)[0]: pygame.mixer.Sound(file=os.path.join(files, name)) for name in os.listdir(files)
            }
    return sounds


def set_volume(volume, category=None):
    """Sets the volume for all sound objects unless category is specified."""
    global SOUNDS
    volume /= 100  # 'set_volume' takes a float between 0.0 to 1.0.

    if category is None:
        VOLUME["main"] = volume
        for dictionary in SOUNDS.values():
            for sound in dictionary.values():
                sound.set_volume(volume)
    else:
        for sound in SOUNDS[category.lower()]:
            sound.set_volume(volume)


def change_volume(delta_volume, category=None):
    """Changes the volume for all sound objects unless category is specified."""
    global SOUNDS

    if category is None:
        VOLUME["main"] += delta_volume
        VOLUME["main"] = max(0, min(VOLUME["main"], 100))
        for dictionary in SOUNDS.values():
            for sound in dictionary.values():
                sound.set_volume(VOLUME["main"] / 100)
    else:
        for sound in SOUNDS[category.lower()]:
            sound.set_volume(sound.get_volume() + delta_volume)


def load_sprites():
    sprites = {}
    map_ = pygame.image.load("sprites/map.png").convert_alpha()
    characters = pygame.image.load("sprites/sprites.png").convert_alpha()
    character_list = [characters.subsurface(pygame.Rect((x * TILE_WIDTH * 2, y * TILE_HEIGHT * 2), (32, 32)))
                      for y in range(7) for x in range(8)]

    sprites['map'] = map_
    sprites['blinky'] = character_list[0:8]
    sprites['inky'] = character_list[8:16]
    sprites['pinky'] = character_list[16:24]
    sprites['clyde'] = character_list[24:32]
    sprites['eaten'] = character_list[32:36]
    sprites['frightened'] = character_list[36:40]
    sprites['pacman'] = character_list[40:43]
    sprites['death'] = character_list[40:48] + character_list[50:51]
    sprites['fruit'] = character_list[49]
    return sprites


def get_tile_index(position):
    return position[1] // TILE_HEIGHT, position[0] // TILE_WIDTH


def get_position(tile_index, offset='center'):
    topleft_pos = (tile_index[1] * TILE_HEIGHT, tile_index[0] * TILE_WIDTH)
    rect = pygame.Rect(topleft_pos, TILE_SIZE)
    return getattr(rect, offset, topleft_pos)

TILE_SIZE = TILE_WIDTH, TILE_HEIGHT = (16, 16)
COLUMNS, ROWS = 28, 36  # 36 rows x 28 columns
SIZE = WIDTH, HEIGHT = (COLUMNS * TILE_WIDTH, ROWS * TILE_HEIGHT)
SCREEN = pygame.display.set_mode(SIZE)
FPS = 120
CLOCK = pygame.time.Clock()
SPRITES = load_sprites()
SOUNDS = load_sounds()
VOLUME = {"main": 100}

MUSIC = [
    "sounds/music/As I Lay Dying - Through Struggle Lyrics.wav",
    "sounds/music/As I Lay Dying - The Sound of Truth.wav"
]

EVENTS = {
    "chase": pygame.event.Event(pygame.USEREVENT, {}),
    "scatter": pygame.event.Event(pygame.USEREVENT + 1, {}),
    "frightened": pygame.event.Event(pygame.USEREVENT + 2, {}),
    "unfrightened": pygame.event.Event(pygame.USEREVENT + 3, {}),
    "return": pygame.event.Event(pygame.USEREVENT + 4, {}),
    "start": pygame.event.Event(pygame.USEREVENT + 5, {})
}


SPAWNS = {
    "pacman": (224, 424),
    "blinky": (224, 232),
    "inky": (192, 280),
    "pinky": (224, 280),
    "clyde": (256, 280),
}

HOUSE_POS = {
    "blinky": (232, 280),
    "inky": (200, 280),
    "pinky": (232, 280),
    "clyde": (264, 280),
}

# HOUSE_POS = {  # Exact
#     "blinky": (224, 280),
#     "inky": (192, 280),
#     "pinky": (224, 280),
#     "clyde": (256, 280),
# }

SCATTER_POS = [(8, 8), (8, 568), (440, 8), (440, 568)]
