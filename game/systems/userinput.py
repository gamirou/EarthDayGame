import random
import pygame

from lib.system import System

class UserInputSystem(System):
    """This system updates the game based on inputs"""

    def __init__(self):
        self.increasing_vel = 1
        self.timer_started = False
        self.passed_time = 0
        self.start_time = 0
        self.time_when_paused = 20

    def update(self, game, dt: float, events):
        keysdown = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        pause_btn = game.items["pause"]
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                is_x_in_range = mouse_pos[0] > pause_btn["rect"][0] and mouse_pos[0] < pause_btn["rect"][0] + pause_btn["rect"][2]
                is_y_in_range = mouse_pos[1] > pause_btn["rect"][1] and mouse_pos[1] < pause_btn["rect"][1] + pause_btn["rect"][3]
                if is_x_in_range and is_y_in_range:
                    game.paused = not game.paused

                    if not game.paused:
                        game.start_time = pygame.time.get_ticks()
                    else:
                        self.time_when_paused = game.remaining_time

        if game.remaining_time <= 0:
            game.over = True

        trash = game.items["trash"]

        if not game.paused:
            if trash["falling"] == False:
                # Pick a different trash
                trash["index"] = random.randint(0, 8)
                # Starting y-point
                trash["pos"][1] = 50
                # Random x-point
                trash["pos"][0] = random.randint(0, 
                                                game.framework.dimensions[0] - 
                                                (trash["sprite"].scale * trash["sprite"].tile_size)
                                                ) 

                trash["falling"] = True
            else:
                # Constraining the increasing velocity
                self.increasing_vel = self.increasing_vel + (dt * 0.05) if self.increasing_vel <= 5 else self.increasing_vel
                trash["pos"][1] += 10 * self.increasing_vel

                if trash["pos"][1] >= game.framework.dimensions[1]:
                    trash["falling"] = False
                    game.wrong += 1
            
            # Change x position based on user input
            if keysdown[pygame.K_LEFT]:
                trash["pos"][0] -= 55
            elif keysdown[pygame.K_RIGHT]:
                trash["pos"][0] += 55
            elif keysdown[pygame.K_DOWN]:
                trash["pos"][1] += 50
            
            # Constrain x value
            if trash["pos"][0] > game.framework.dimensions[0] - (trash["sprite"].scale * trash["sprite"].tile_size):
                trash["pos"][0] = game.framework.dimensions[0] - (trash["sprite"].scale * trash["sprite"].tile_size)
            elif trash["pos"][0] < 0:
                trash["pos"][0] = 0

            self.passed_time = pygame.time.get_ticks() - game.start_time
            game.remaining_time = self.time_when_paused - (self.passed_time/1000)