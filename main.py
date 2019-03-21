import pygame
import itertools
import math
import settings
from character import Player, Ghost, Point, Enegizer
from level.level import TileMap
import text



import asyncio
import websockets
from functools import partial
from classActivity import mainly



pygame.init()
pygame.mixer.init()


class Mode:

    def __init__(self, mode_queue, timer_queue, repeat=-1):
        self.mode_queue = mode_queue
        self.timer_queue = timer_queue
        self.repeat = repeat
        self.kill = False
        self.time = 0
        self.mode_index = 0
        self.time_index = 0

    def update(self, dt, *ignored):
        if self.kill:
            return None
        self.time += dt
        if self.time >= self.timer_queue[self.time_index]:
            self.time = self.time - self.timer_queue[self.time_index]
            self.time_index = (self.time_index + 1) % len(self.timer_queue)
            self.mode_index = (self.mode_index + 1) % len(self.mode_queue)
            if self.mode_index == 0:
                self.repeat -= 1 if self.repeat > 0 else 0
            if self.repeat == 0:
                self.kill = True
                return None
        return self.mode_queue[self.mode_index]


def change_music(track=0):
   # pygame.mixer.music.stop()
   # pygame.mixer.music.load(settings.MUSIC[track])
     pass


def add_points(tile_map):
    energizer_tiles = [(6, 1), (6, 26), (26, 1), (26, 26)]
    energizer_pos = [settings.get_position(x, offset="topleft") for x in energizer_tiles]
    empty_pos = list(itertools.product(range(12, 23), range(7, 21)))  # Square by the house.
    for tile in tile_map.tile.values():
        if settings.get_tile_index(tile.rect.topleft) in empty_pos:
            continue
        if tile.is_any_type("path", "restricted") and 0 <= tile.rect.x < settings.WIDTH:
            if any(tile.rect.collidepoint(pos) for pos in energizer_pos):
                tile.content.add(Enegizer(tile.rect))
            else:
                tile.content.add(Point(tile.rect))


def collision(player, ghosts, tile_map, text_group, mode, score, clock):  # Maybe add to Player class?
    for object_ in tile_map[player.tile_index].content.copy():
        if type(object_) == Ghost:
            if mode in ("frightened", "unfrightened") and object_.frightened:
                hit_text = text.FadingText(text="HAHA!", fade_out=0.5, pos=player.rect.topright, color=(255, 255, 0),
                                           font=pygame.font.SysFont(None, 16), origin="bottomleft")
                text_group.add(hit_text)
                object_.frightened = False
                object_.dead = True
            elif not object_.dead:
                delay(1, clock)
                player.dead = True
        elif type(object_) == Point:
            score += 1
            tile_map[player.tile_index].content.remove(object_)
            object_.kill()
        elif type(object_) == Enegizer:
            score += 10
            tile_map[player.tile_index].content.remove(object_)
            object_.kill()
            mode = "frightened"
            change_frightened(ghosts)
    return mode, score


def show(ghosts, target=False, house=False):
    for ghost in ghosts:
        color = [(255, 0, 0), (0, 255, 255), (255, 100, 255), (150, 150, 50)][ghost.ID]
        if target:
            pygame.draw.circle(settings.SCREEN, color, (int(ghost.end_target[0]), int(ghost.end_target[1])), 4)
        if house:
            house_rect = pygame.Rect((0, 0), settings.TILE_SIZE)
            house_rect.center = settings.HOUSE_POS[ghost.NAME[ghost.ID]]
            pygame.draw.rect(settings.SCREEN, color, house_rect, 1)


def draw_grid(screen, tile_map):
    for tile in tile_map.tile.values():
        pygame.draw.rect(screen, (100, 100, 100), tile.rect, 1)


def change_frightened(ghosts):
    for ghost in ghosts:
        if not ghost.dead:
            ghost.frightened = True


def change_unfrightened(ghosts):
    for ghost in ghosts:
        ghost.frightened = False


def delay(seconds, game_clock):
    while seconds > 0:
        dt = game_clock.tick(20) / 1000
        seconds -= dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()





async def handle_message(message):
   # classMainlyInstance.writeMessage(message)
	pass
async def consumer_handler( classMainlyInstance,websocket, path):
	print("IN")
	
	while True:
		try:
			message = await websocket.recv()
			await classMainlyInstance['classIn'].writeMessage(message)
			
			await handle_message(message)

		except Exception:
			pass

	print("OUT")








async def main(TabinstanceClassD):

   
    screen = settings.SCREEN
    clock = settings.CLOCK
    fps = settings.FPS

    tile_map = TileMap()
    add_points(tile_map)
    Player.TabinstanceClassD = TabinstanceClassD

    player = Player(position=settings.SPAWNS["pacman"], )
    ghosts = pygame.sprite.Group(Ghost(position=settings.SPAWNS[name]) for name in ["blinky", "inky", "pinky", "clyde"])
    single_text = pygame.sprite.GroupSingle()
    setting_text = pygame.sprite.GroupSingle()
    setting_text_pos = (screen.get_width() // 2 - 9, 12)
    font = pygame.font.SysFont(None, 32)

    # Starting with scatter and alternating in following interval (in secs):
    # Level 1: 7, 20, 7, 20, 5, 20, 5, inf;
    # Level 2-4: 7, 20, 7, 20, 5, 1033, 1 / 60, inf;
    # Level 5+: 5, 20, 5, 20, 5, 1037, 1 / 60, inf;
    normal_mode = Mode(["scatter", "chase"], [7, 20, 7, 20, 5, 20, 5, math.inf])
    frighten_mode = Mode(["frightened", "unfrightened"], [5, 3], 1)
    mode = "scatter"

    score = 0
    speed_factor = 1.2  # How fast to run the game.
    time = 0
    start_timer = 2
    paused = False
    started = False
    music = False
    grid = False
    see_target = False
    while 1:
        await asyncio.sleep(0)
        dt = (clock.tick(fps) / 1000)  # "dt" is the time between each loop in seconds.
        time += dt if started and not paused and not player.dead else 0
        dt *= speed_factor  # "time" shouldn't be affected, the rest should.

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit()
                elif event.key == pygame.K_f:
                    fps = (fps % 120) + 20
                    setting_text.add(text.FadingText("FPS: {}".format(fps), fade_out=1, pos=setting_text_pos, origin="midtop",
                                                     font=font, color=(255, 255, 255)))
                elif event.key == pygame.K_r or event.key == pygame.K_SPACE:
                    for tile in tile_map.tile.values():
                        for ghost in ghosts:
                            if ghost in tile.content:
                                tile.remove_content(ghost)
                    Ghost.ID = 0
                    player = Player(position=settings.SPAWNS["pacman"])
                    ghosts = pygame.sprite.Group(
                        Ghost(position=settings.SPAWNS[name]) for name in ["blinky", "inky", "pinky", "clyde"]
                    )
                    start_timer = 2
                    started = False
                elif event.key == pygame.K_p:
                    pygame.mixer.music.unpause() if paused else pygame.mixer.music.pause()
                    paused = not paused
                    temp = "Paused" if paused else "Unpaused"
                    setting_text.add(text.FadingText(temp, fade_out=1, pos=setting_text_pos, origin="midtop",
                                                     font=font, color=(255, 255, 255)))
                elif event.key == pygame.K_1:
                    change_music(track=0)
                    setting_text.add(text.FadingText(settings.MUSIC[0][29:46], fade_out=1, pos=setting_text_pos, origin="midtop",
                                                     font=font, color=(255, 255, 255)))
                elif event.key == pygame.K_2:
                    change_music(track=1)
                    setting_text.add(text.FadingText(settings.MUSIC[1][29:48], fade_out=1, pos=setting_text_pos, origin="midtop",
                                                     font=font, color=(255, 255, 255)))
                elif event.key == pygame.K_3:
                    pygame.mixer.music.stop()
                    setting_text.add(text.FadingText("Paused music", fade_out=1, pos=setting_text_pos, origin="midtop",
                                                     font=font, color=(255, 255, 255)))
                elif event.key == pygame.K_g:
                    grid = not grid
                    setting_text.add(text.FadingText("Grid", fade_out=1, pos=setting_text_pos, origin="midtop",
                                                     font=font, color=(255, 255, 255)))
                elif event.key == pygame.K_t:
                    see_target = not see_target
                    setting_text.add(text.FadingText("Target", fade_out=1, pos=setting_text_pos, origin="midtop",
                                                     font=font, color=(255, 255, 255)))
                elif event.key == pygame.K_x:
                    speed_factor = (speed_factor + 0.1) % 2.05 if 2 > speed_factor >= 1 else 1
                    setting_text.add(text.FadingText("Speed: {0:.1f}".format(speed_factor), fade_out=1, pos=setting_text_pos, origin="midtop",
                                                     font=font, color=(255, 255, 255)))
            elif event.type == pygame.QUIT:
                quit()

        if not paused and started and not player.dead:  # Do game updates and logic checks
            if score >= 60 and not Ghost.SPAWN[3]:  # 60
                Ghost.SPAWN[3] = True
                print("Clyde's coming out!")
            if score >= 30 and not Ghost.SPAWN[1]:  # 30
                Ghost.SPAWN[1] = True
                print("Inky's coming out!")

            if mode in ("frightened", "unfrightened"):
                mode = frighten_mode.update(dt)
                if mode is not None:
                    Ghost.MODE = Ghost.MODES[mode]
                else:
                    frighten_mode = Mode(["frightened", "unfrightened"], [5, 3], 1)
                    change_unfrightened(ghosts)
            else:
                mode = normal_mode.update(dt)
                Ghost.MODE = Ghost.MODES[mode]
            player.update(tile_map, dt)
            ghosts.update(tile_map, dt, player, ghosts)
            Point.instances.update(dt)
            mode, score = collision(player, ghosts, tile_map, single_text, mode, score, clock)
            single_text.update(dt)

        elif player.dead:
            player.animate(dt)

        tile_map.draw(screen)
        text.put_text(screen, "Score: {0}".format(score), pos=(-128, 36), origin="bottomleft")
        text.put_text(screen, "Time: {0:.1f}".format(time), pos=(16, 36), origin="bottomleft")
        setting_text.update(dt)
        setting_text.draw(screen)
        Point.instances.draw(screen)
        if grid:
            draw_grid(screen, tile_map)
        if see_target:
            show(ghosts, target=True, house=True)
        if not player.dead:
            ghosts.draw(screen)
        single_text.draw(screen)
        screen.blit(player.image, player.rect)
        if not started:
            start_timer -= dt
            text.put_text(screen, "READY!", (224, 328), color=(255, 255, 0), font=pygame.font.SysFont(None, 32, 1, 1))
            if not music:
                change_music(track=0)
                music = True
            if start_timer <= 0:
                start_timer = 2
                started = True
        if len(Point.instances) <= 0:
            text.put_text(screen, "WON!", settings.SPAWNS["pacman"])
            pygame.display.update()
            # delay(2, clock)  # Will delay every update.
        pygame.display.update()


if __name__ == '__main__':

    classMainlyInstance = mainly()
    dictclass = dict()
    dictclass['classIn'] = classMainlyInstance

    e = partial(consumer_handler,dictclass)
    start_server = websockets.serve(e, 'localhost', 8765)

    asyncio.ensure_future(start_server)
    asyncio.ensure_future(main(dictclass))
    
    asyncio.get_event_loop().run_forever()
    
