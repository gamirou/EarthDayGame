import pygame
import os

COLOURS = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
}


# To read a file, you need to write: open(Game.directories[folder-name] + "\\file-name", mode)
def get_directories():
    # Storing all directories from the parent folder in a dictionary
    directory = os.getcwd()
    os.chdir("..")
    paths = [os.path.join(directory, o) for o in os.listdir(directory) if
             os.path.isdir(os.path.join(directory, o))]

    directories = {}

    for subDir in paths:
        folder = subDir.split("\\")[-1]
        directories[folder] = subDir

    return directories


class Engine:
    directories = get_directories()

    def __init__(self, width, height, title, image=None):
        self.WIDTH = width
        self.HEIGHT = height
        self.TITLE = title

        self.EVENTS = {
            "QUIT": pygame.QUIT,
            "KEYDOWN": pygame.KEYDOWN,
            "KEYUP": pygame.KEYUP,

            # Movement keys
            "K_DOWN": pygame.K_DOWN,
            "K_UP": pygame.K_UP,
            "K_LEFT": pygame.K_LEFT,
            "K_RIGHT": pygame.K_RIGHT
        }

        self.exit = False

        self.display = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption(self.TITLE, image) if image else pygame.display.set_caption(self.TITLE)

    def rect(self, colour, info):
        pygame.draw.rect(self.display, colour, info)

    def background(self, colour):
        self.display.fill(colour)

    @staticmethod
    def update():
        pygame.display.update()

    @staticmethod
    def get_events():
        return pygame.event.get()

    @staticmethod
    def quit():
        pygame.quit()