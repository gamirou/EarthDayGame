import pygame

from lib.system import System
from lib.spritesheet import SpriteSheet

class RenderSystem(System):
    """This system draws any entity with a SpriteSheet component."""

    def __init__(self, screen):
        self.screen = screen
        self.image_cache = {}
        self.steps = 0

        font_path = 'assets/fonts/nyala.ttf'
        self.font = pygame.font.Font(font_path, 45)
        self.paused_font = pygame.font.Font(font_path, 105)

    def update(self, game, dt: float, events):
        # Step through 15 sprite frames each second
        self.steps += dt
        frame = int(self.steps // (1.0 / 15))

        # We need to include gamestate when drawing background to scale the image
        self.draw_background(game)

        # Draw all the entities
        for key in game.items:
            item = game.items[key]

            # Draw pause button
            if "sprite" not in item.keys():
                for pos in item["pos"]:
                    pygame.draw.rect(self.screen, (0, 0, 0), pos)
                continue

            if isinstance(item["index"], list):
                # Draw more items from the same sprite (bins)
                if len(item["index"]) != len(item["pos"]):
                    raise ValueError("Pos and index lists need to have the same length")

                for i in range(len(item["index"])):
                    self.screen.blit(self.get_image(item["sprite"], item["index"][i]), item["pos"][i])
            else:
                # Draw one item only (trash)
                self.screen.blit(self.get_image(item["sprite"], item["index"]), item["pos"])    
        
        # Text and colour
        texts = [("Trash successfully recycled: " + str(game.right), (0, 0, 0), 0),
                 ("Trash not recycled: " + str(game.wrong), (0, 0, 0), 0),
                 ("Name: " + game.name, ((66, 179, 244) if game.gender == "Boy" else (244, 66, 241)), 0),
                 ("Time remaining: " + str(int(game.remaining_time)), (0, 0, 0), 0)]

        top_offset = 0
        for text in texts:
            rendered_text = self.font.render(text[0], False, text[1])                
            self.screen.blit(rendered_text, (text[2], top_offset))
            
            top_offset += 30

        if game.paused:
            rendered_text = self.paused_font.render("PAUSED", False, (255, 255, 255))
            self.screen.blit(rendered_text, (game.framework.dimensions[0]/2-180, game.framework.dimensions[1]/2-105))

    def draw_background(self, game):
        self.screen.blit(self.get_image(game.background, 0, game), (0, 0))

    def get_image(self, spritesheet, index, game=None):
        # Ideally, we cache so we only process a file once
        if spritesheet.path not in self.image_cache or game is not None:
            # Load from file
            sheet_img = pygame.image.load(spritesheet.path).convert_alpha()
            
            # Scale the image
            if spritesheet.scale != 1:
                scaled_size = (int(spritesheet.scale * sheet_img.get_width()), int(spritesheet.scale * sheet_img.get_height()))
                sheet_img = pygame.transform.scale(sheet_img, scaled_size)

            if spritesheet.path.endswith("Background.fw.png"):
                # This happens when resizing
                if sheet_img.get_size() != game.framework.dimensions:
                    old_background_tile = game.background.tile_size

                    game.background.tile_size = game.framework.dimensions
                    sheet_img = pygame.transform.scale(sheet_img, game.framework.dimensions)

                    # Fixing the bins too
                    # Get the image
                    sheet_bins = pygame.image.load(game.items["bins"]["sprite"].path).convert_alpha()
                    
                    curr_bin_tile_size = game.items["bins"]["sprite"].tile_size
                    # Make a new tile size using the formula bw' = bw * (BW' / BW) 
                    new_tile_size = (int((curr_bin_tile_size[0] * 6) * (game.background.tile_size[0] / old_background_tile[0]) / 6),
                                     int(curr_bin_tile_size[1] * (game.background.tile_size[1] / old_background_tile[1])))

                    # Scale the real image to our new sizes (width = tw * 6 because the sprite has 6 images)
                    sheet_bins = pygame.transform.scale(sheet_bins, (new_tile_size[0] * 6, new_tile_size[1]))
                    game.items["bins"]["sprite"].tile_size = new_tile_size

                    game.items["bins"]["pos"] = [
                        [new_tile_size[0], game.framework.dimensions[1] - new_tile_size[1]],
                        [new_tile_size[0] + (game.framework.dimensions[0] - 3 * new_tile_size[0]) / 2, game.framework.dimensions[1] - new_tile_size[1]],
                        [game.framework.dimensions[0] - 2 * new_tile_size[0], game.framework.dimensions[1] - new_tile_size[1]]
                    ]

                    # Now caching the new images to our array
                    images = []
                    for y in range(0, sheet_bins.get_height(), new_tile_size[1]):
                        for x in range(0, sheet_bins.get_width(), new_tile_size[0]):
                            bounds = pygame.Rect(x, y, new_tile_size[0], new_tile_size[1])
                            images.append(sheet_bins.subsurface(bounds))
                    self.image_cache[game.items["bins"]["sprite"].path] = images

                    # Getting new pause button position
                    game.items["pause"]["pos"]=[
                        [game.framework.dimensions[0] - 50, 10, 10, 50], 
                        [game.framework.dimensions[0] - 25, 10, 10, 50]
                    ]
                    game.items["pause"]["rect"] = [game.framework.dimensions[0]-50, 10, 35, 50]

                else:
                    if spritesheet.path in self.image_cache:
                        return self.image_cache[spritesheet.path][index]

            if isinstance(spritesheet.tile_size, tuple):
                tile_width = spritesheet.tile_size[0]
                tile_height = spritesheet.tile_size[1]
            else:
                tile_width = spritesheet.tile_size
                tile_height = spritesheet.tile_size
            
            # Check the file can be divided right
            if sheet_img.get_width() % tile_width != 0 or sheet_img.get_height() % tile_height != 0:
                print(sheet_img.get_width(), tile_width)
                raise ValueError('Spritesheet width and height are not a multiple of its tile size')
            
            # Partition into sub-images
            images = []
            for y in range(0, sheet_img.get_height(), tile_height * spritesheet.scale):
                for x in range(0, sheet_img.get_width(), tile_width * spritesheet.scale):
                    bounds = pygame.Rect(x, y, tile_width * spritesheet.scale, tile_height * spritesheet.scale)
                    images.append(sheet_img.subsurface(bounds))
            self.image_cache[spritesheet.path] = images

        return self.image_cache[spritesheet.path][index]