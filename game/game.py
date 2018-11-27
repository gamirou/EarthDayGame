import pygame

from game.systems.render import RenderSystem
from game.systems.userinput import UserInputSystem
from game.systems.collision import CollisionSystem

from lib.spritesheet import SpriteSheet


class GameState:
    """Our core code.
    
    Our game is made up of entities, with individual properties and systems:
    - Items have basic properties in a dictionary:
      * Trash: {"sprite": SpriteSheet(), "pos": [[0, 2], [2, 3]]}
    - Systems update all of our entities to make things tick-over, e.g.:
      * CollisionSystem
      * RenderSystem
      * UserInputSystem
    """
    systems = []

    def __init__(self, framework, name, gender):
        """Creates a GameState to fit our framework, with some information about ourselves."""
        self.framework = framework
        self.screen = framework.screen
        self.renderSystem = RenderSystem(self.screen)
        self.collisionSystem = CollisionSystem()
        
        self.name = name
        self.gender = gender

        self.frames = 0
        self.paused = False
        self.over = False
        self.remaining_time = 120
        self.start_time = pygame.time.get_ticks()

        self.items = {}
        self.right = 0
        self.wrong = 0
        self.background = SpriteSheet("assets/images/Background.fw.png", self.framework.dimensions)

        # Add all systems we want to run
        self.systems.extend([
            # TODO: To add a profile somehow to add to the leaderboard
            #ProfileSystem(name, gender),
            UserInputSystem(),
            self.collisionSystem,
            self.renderSystem,
        ])

        self.items["trash"] = {
            "sprite": SpriteSheet("assets/images/TrashSprite.fw.png", 60, 2),
            "index": 0,
            "pos": [500, 50],
            "offset": [0, 0],
            "falling": True,
        }

        # There will be three bins
        self.items["bins"] = {
            "sprite": SpriteSheet("assets/images/BinSprite.fw.png", (144, 188)),
            "index": [0, 2, 4],
            "pos": [[144, 577], [603, 577], [1062, 577]],
            "offset": [144, 188]
        }

        self.items["pause"] = {
            "pos": [[self.framework.dimensions[0] - 50, 10, 10, 50], [self.framework.dimensions[0] - 25, 10, 10, 50]],
            "rect": [self.framework.dimensions[0]-50, 10, 35, 50],
            "clicked": False
        }

    def update(self, dt: float, events):
        """This code gets run 60fps. All of our game logic stems from updating
        our systems on our entities."""

        # Update our systems
        if not self.over:
            for system in self.systems:
                system.update(self, dt, events)
        else:
            user = {"name":self.name, "gender":self.gender}
            score = {
                "right": self.right,
                "wrong": self.wrong,
                "percentage": str(round(self.right/(self.right+self.wrong) * 100, 2))
            }
            self.framework.enter_leaderboard(user, score)