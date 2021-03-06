import pygame, sys, platform, os

from game.game import GameState
from lib.menu import MenuState
from leaderboard.leaderboard import LeaderboardState

class Framework:
    """The core state of our app."""

    caption = 'Earth Day 2019'
    
    dimensions = (1360, 765)

    fps = 60
    running = True
    clock = pygame.time.Clock()

    def __init__(self):
        # Initialise pygame
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        pygame.display.set_caption(self.caption)
        self.screen = pygame.display.set_mode(self.dimensions, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)

        # Delegate
        self.state = MenuState(self)

    def main_loop(self):
        # Initial tick so our first tick doesn't return all the time since __init__
        self.clock.tick()

        # While we haven't been stopped
        while self.running:
            # Black-out the screen
            self.screen.fill((77, 140, 242))

            # Count how long has passed since we last did this
            dt = self.clock.tick(self.fps) / 1000.0

            # Grab any keyboard/window events
            events = [event for event in pygame.event.get()]

            for event in events:
                # The user probably closed the window, let's quit
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                if event.type == pygame.VIDEORESIZE:
                    SCREENSIZE = (event.w,event.h)
                    pygame.display.set_mode(SCREENSIZE, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
                    self.dimensions = SCREENSIZE

            # Update the current state
            self.state.update(dt, events)

            # Display any rendered updates
            pygame.display.update()

        # We've stopped, close pygame, kill everything
        pygame.display.quit()
        if platform.system() == "Windows":
            os.system("taskkill /f /pid "+str(os.getpid()))
        elif platform.system() == "Linux":
            pygame.quit()
            sys.exit()

    def enter_game(self, name, gender):
        self.state = GameState(self, name, gender)

    def enter_leaderboard(self, user: dict, score: dict):
        self.state = LeaderboardState(self, user, score)