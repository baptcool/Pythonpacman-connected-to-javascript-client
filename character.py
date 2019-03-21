import pygame
import settings
import math
from vector import Vector2D
from animation import Animation, OneTimeAnimation


class Player(pygame.sprite.Sprite):
    TabinstanceClassD = object()
    def __init__(self, position=(0, 0)):
        super(Player, self).__init__()
        self.animation = {
            "right": Animation((pygame.transform.rotate(sprite, -90) for sprite in settings.SPRITES["pacman"]), 0.17),
            "left": Animation((pygame.transform.rotate(sprite, 90) for sprite in settings.SPRITES["pacman"]), 0.17),
            "up": Animation((pygame.transform.rotate(sprite, 180) for sprite in settings.SPRITES["pacman"]), 0.17),
            "down": Animation((pygame.transform.rotate(sprite, 0) for sprite in settings.SPRITES["pacman"]), 0.17),
            "death": OneTimeAnimation(settings.SPRITES["death"], 0.17)
        }
        self.image = self.animation["right"].sprites[0]
        self.rect = self.image.get_rect(center=position)
        self.position = Vector2D(*position)
        self.tile_index = settings.get_tile_index(position)
        self.moving = False
        self.target = self.position
        self.direction = Vector2D(0, 0)
        self.radius = self.rect.width // 3
        self.energized = True
        self.dead = False

    @staticmethod
    def get_direction():
        debugServer=0
        if debugServer == 0:
                
            frunc =  Player.TabinstanceClassD['classIn']#.lireMessage()

            if frunc.presenceMessage():
                key  = frunc.lireMessage()
                if key == 0:
                    return None
                if key == "U":
                    return 0, -1
                elif key == "U'":
                    return 0, 1
                elif key == "R":
                    return 1, 0
                elif key == "R'":
                    return -1, 0
                return None
            else:
                return None
        else:

            key = pygame.key.get_pressed()
            if key[pygame.K_a] or key[pygame.K_LEFT]:
                return -1, 0
            elif key[pygame.K_w] or key[pygame.K_UP]:
                return 0, -1
            elif key[pygame.K_d] or key[pygame.K_RIGHT]:
                return 1, 0
            elif key[pygame.K_s] or key[pygame.K_DOWN]:
                return 0, 1
            return None

    def set_target(self, tile_map, col_offset=0, row_offset=0):
        try:
            tile = tile_map.get_tile(self.tile_index, col_offset, row_offset)
        except KeyError:
            self.teleport()
            return True

        if tile.is_any_type("path", "restricted", "tunnel"):
            tile.content.add(self)
            row, column = self.tile_index
            tile_map[row, column].remove_content(self)
            self.target = Vector2D(*tile.rect.center)
            self.moving = True
            self.direction = (self.target - self.position).normalize()
            return True
        return False

    def teleport(self):
        if self.tile_index[1] == -2:
            self.tile_index = (self.tile_index[0], 28)
        else:
            self.tile_index = (self.tile_index[0], -1)
        self.position = Vector2D(*settings.get_position(self.tile_index))

    def move(self, dt):
        distance = self.target - self.position
        speed = 120 * dt
        self.position += distance if abs(distance) <= speed else distance.normalize() * speed
        self.rect.center = self.position[0], self.position[1]

    def stop_if_arrived(self):
        if self.position == self.target:
            self.moving = False
            self.tile_index = settings.get_tile_index(self.position)

    def animate(self, dt):
        if self.dead:
            image = self.animation["death"].update(dt)
            if image is not None:
                self.image = image
            return
        direction = direction_as_int(self.direction)
        if direction == 1:
            image = self.animation["left"].update(dt)
        elif direction == 2:
            image = self.animation["up"].update(dt)
        elif direction == 3:
            image = self.animation["right"].update(dt)
        elif direction == 4:
            image = self.animation["down"].update(dt)
        else:
            return
        self.image = image

    def update(self, tile_map, dt, *ignore):
        if not self.moving:
            asked_direction = self.get_direction()
            if not asked_direction or not self.set_target(tile_map, asked_direction[0], asked_direction[1]):
                self.set_target(tile_map, *self.direction)
        self.move(dt)
        self.animate(dt)
        self.stop_if_arrived()


# ---------------------------------------------------------------------------------------------------------------------


class Ghost(pygame.sprite.Sprite):

    ID = 0
    NAME = {0: "blinky", 1: "inky", 2: "pinky", 3: "clyde"}
    MODES = {"chase": 0, "scatter": 1, "frightened": 2, "unfrightened": 3}
    MODE = MODES["chase"]
    SPAWN = [True, False, True, False]  # When the ghost are supposed to spawn. The index is the ghosts ID.

    def __init__(self, position=(0, 0)):
        super(Ghost, self).__init__()
        self.ID = Ghost.ID
        Ghost.ID += 1
        self.sprites = settings.SPRITES[Ghost.NAME[self.ID]]
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(center=position)
        self.prev_tile_index = (0, 0)
        self.tile_index = settings.get_tile_index(position)
        self.direction = Vector2D(0, 0)
        self.moving = False  # replace with abs(self.direction) == 0
        self.position = Vector2D(*position)
        self.target = self.position
        self.end_target = self.position
        self.time = 0
        self.speed = 80
        self.dead = False
        self.frightened = False
        self.mode = 0

    def get_walkable_tiles(self, tile_map):
        """Ghost cannot move to a tile they're already on or to the house/door if they"re outside."""
        neighbours = tile_map.get_neighbours(self.tile_index)
        current_tile = tile_map[self.tile_index]

        if self.dead or current_tile.is_type("house"):
            return [tile for tile in neighbours if ((not tile.is_type("wall")) and not tile.contains(self))]
        else:
            return [tile for tile in neighbours if ((not tile.is_any_type("door", "wall")) and not tile.contains(self))]

    def get_target_tile(self, walkable_tiles, current_tile):
        if len(walkable_tiles) == 1:
            return walkable_tiles[0]
        target_distance = math.inf
        target_tile = None
        for tile in walkable_tiles:
            distance = abs(Vector2D(*tile.rect.center) - self.end_target)
            if distance < target_distance:
                # Can't move up on restricted tiles. Ignored if eaten.
                if current_tile.is_type("restricted") and tile.rect.y < self.rect.y and not self.dead:
                    continue
                target_distance = distance
                target_tile = tile
        return target_tile

    def handle_tile_content(self, target_tile, tile_map):
        """Removes itself from the previous tile and adds itself to the current and next tile."""
        target_tile.add_content(self)
        tile_map[self.tile_index].add_content(self)
        tile_map[self.prev_tile_index].remove_content(self)

    def set_target(self, target_tile):
        self.prev_tile_index = self.tile_index
        self.target = Vector2D(*target_tile.rect.center)
        self.moving = True
        self.direction = (self.target - self.position).normalize()

    def set_end_taget(self, tile_map, pacman, ghosts):
        """
        Sets the destination the ghost is heading ultimately. Not to be confused with "set_target" which sets the target
        for the next tile in order to reach the end target.
        """
        if self.dead:
            self.end_target = settings.HOUSE_POS[Ghost.NAME[self.ID]]
        elif tile_map[self.tile_index].is_type("house"):  # If the ghost exit the house it will change end_target.
            self.end_target = Vector2D(224, 232)  # So the ghosts can move outside,
        elif self.frightened:
            # self.end_target = 2 * self.position - pacman.position
            # Added self.position - pacman.position to keep the end_target one tile away from ghost.
            # Else it would enter the end_target when it got eaten and immediately go back.
            self.end_target = 2 * self.position - pacman.position + self.direction * settings.TILE_WIDTH
        elif Ghost.MODE == Ghost.MODES["chase"]:
            if Ghost.NAME[self.ID] == "blinky":
                self.end_target = pacman.position
            elif Ghost.NAME[self.ID] == "inky":
                blinky = None
                for ghost in ghosts:
                    if ghost.ID == 0:
                        blinky = ghost
                a = pacman.position + pacman.direction * settings.TILE_WIDTH * 2  # Two tiles ahead of pacman.
                b = a - blinky.position + a
                self.end_target = b
                # self.end_target = pacman.position + pacman.direction * settings.TILE_WIDTH * 4  # Temp
            elif Ghost.NAME[self.ID] == "pinky":
                # Four tiles ahead of pacman.
                self.end_target = pacman.position + pacman.direction * settings.TILE_WIDTH * 4
            elif Ghost.NAME[self.ID] == "clyde":
                if abs(self.position - pacman.position) > settings.TILE_WIDTH * 8:  # Pacman more than 8 tiles away.
                    self.end_target = pacman.position
                else:
                    self.end_target = Vector2D(8, 560)  # Scatter corner
        else:  # Ghost.MODE == Ghost.MODES["scatter"]:
            self.end_target = Vector2D(*settings.SCATTER_POS[self.ID])

    def move(self):
        distance = self.target - self.position
        self.position += distance if abs(distance) <= self.speed else distance.normalize() * self.speed
        self.rect.center = self.position[0], self.position[1]

    def stop_if_arrived(self):
        if self.position == self.target:
            self.moving = False
            self.tile_index = settings.get_tile_index(self.position)
            return True
        return False

    def teleport(self, tile_map):
        """Teleports the ghost between one of the tiles outside the tunnel, depending on the current tile position."""
        row = -2 if self.tile_index[1] == 29 else 28
        self.handle_tile_content(tile_map[(self.tile_index[0], row)], tile_map)
        self.prev_tile_index = self.tile_index
        self.tile_index = (self.tile_index[0], row)
        self.position = Vector2D(*settings.get_position(self.tile_index))

    def change_speed(self, dt, tile_map):
        if self.dead:
            self.speed = 240 * dt
        elif self.frightened:
            self.speed = 40 * dt
        elif tile_map[self.tile_index] in ["tunnel", "house", "door"]:
            self.speed = 40 * dt
        else:
            self.speed = 80 * dt

    def animate(self, dt):
        self.time += dt
        time = self.time % 0.36

        if self.frightened and Ghost.MODE == Ghost.MODES["unfrightened"]:
            if self.time % 0.72 < 0.36:
                self.frightened_animation(time)
            else:
                self.unfrightens_animation(time)
        elif self.frightened:
            self.frightened_animation(time)
        elif self.dead:
            self.eaten_animation()
        else:
            self.normal_animation(time)

    def frightened_animation(self, time):
        if time < 0.18:
            self.image = settings.SPRITES["frightened"][0]
        else:
            self.image = settings.SPRITES["frightened"][1]

    def normal_animation(self, time):
        if time < 0.18:
            self.image = self.sprites[direction_as_int(self.direction) - 1]
        else:
            self.image = self.sprites[direction_as_int(self.direction) + 3]

    def eaten_animation(self):
        self.image = settings.SPRITES["eaten"][direction_as_int(self.direction) - 1]

    def unfrightens_animation(self, time):
        if time < 0.18:
            self.image = settings.SPRITES["frightened"][2]
        else:
            self.image = settings.SPRITES["frightened"][3]

    def update(self, tile_map, dt, pacman, ghosts, *ignore):
        if not self.moving:
            walkable_tiles = self.get_walkable_tiles(tile_map)
            target_tile = self.get_target_tile(walkable_tiles, tile_map[self.tile_index])
            if target_tile:
                self.handle_tile_content(target_tile, tile_map)
                self.set_target(target_tile)
            else:
                return
        self.change_speed(dt, tile_map)
        self.move()
        self.animate(dt)
        if self.stop_if_arrived():
            if self.dead and self.position == self.end_target:
                self.dead = False
            if self.tile_index[1] == -2 or self.tile_index[1] == 29:  # If the ghost is outside the tunnel
                self.teleport(tile_map)
            elif Ghost.SPAWN[self.ID]:  # If the ghost has spawned.
                self.set_end_taget(tile_map, pacman, ghosts)

    def __repr__(self):
        return Ghost.NAME[self.ID]


class Point(pygame.sprite.Sprite):

    instances = pygame.sprite.Group()

    def __init__(self, rect):
        super(Point, self).__init__(Point.instances)
        self.image = pygame.Surface(settings.TILE_SIZE)
        self.radius = rect.width//8
        pygame.draw.circle(self.image, (255, 255, 255), self.image.get_rect().center, self.radius)
        self.image.set_colorkey((0, 0, 0))
        self.rect = rect


class Enegizer(Point):

    def __init__(self, rect):
        super(Enegizer, self).__init__(rect)
        self.radius = rect.width//3
        self.time = 0
        pygame.draw.circle(self.image, (255, 255, 255), self.image.get_rect().center, self.radius)

    def update(self, dt):
        self.time += dt
        if self.time % 0.36 < 0.18:
            pygame.draw.circle(self.image, (255, 255, 255), self.image.get_rect().center, self.radius)
        else:
            pygame.draw.circle(self.image, (0, 0, 0), self.image.get_rect().center, self.radius)


def direction_as_int(direction):
    if direction[0] == -1:
        return 1
    elif direction[1] == 1:
        return 2
    elif direction[0] == 1:
        return 3
    elif direction[1] == -1:
        return 4
    else:
        return 0
