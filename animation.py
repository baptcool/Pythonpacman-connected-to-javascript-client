class Animation:

    def __init__(self, sprites, time_interval):
        self.sprites = tuple(sprites)
        self.time_interval = time_interval
        self.index = 0
        self.time = 0

    def restart_at(self, index):
        self.time = 0
        self.index = index % len(self.sprites)

    def update(self, dt):
        self.time += dt
        if self.time >= self.time_interval:
            self.time = self.time - self.time_interval
            self.index = (self.index + 1) % len(self.sprites)
        return self.sprites[self.index]


class OneTimeAnimation:

    def __init__(self, sprites, time_interval):
        self.sprites = tuple(sprites)
        self.time_interval = time_interval
        self.index = 0
        self.time = 0
        self.dead = False

    def restart_at(self, index):
        self.time = 0
        self.index = index % len(self.sprites)

    def update(self, dt):
        if self.dead:
            return None
        self.time += dt
        if self.time >= self.time_interval:
            self.time = self.time - self.time_interval
            self.index += 1
            if self.index >= len(self.sprites) - 1:
                self.dead = True
        return self.sprites[self.index]


class ConditionalAnimation:

    def __init__(self, sprites, condition):
        self.sprites = sprites
        self.condition = condition

    def update(self, argument):
        return self.sprites[self.condition(argument)]
