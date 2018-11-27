class SpriteSheet:

    def __init__(self, path, tile_size, scale=1, moving=False):
        self.path = path
        self.tiles = {}
        self.tile_size = tile_size
        self.moving = moving
        self.scale = scale