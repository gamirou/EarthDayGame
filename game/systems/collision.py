import pygame

from lib.system import System

class CollisionSystem(System):

    def __init__(self):
        pass

    def update(self, game, dt: float, events):
        trash = game.items["trash"]
        bins = game.items["bins"]

        trash_pos = self.centerPosition(trash["pos"], trash["sprite"].tile_size)

        # TODO: I could check for the smallest distance, but I will do that later
        # I need a formula for bins positioning
        bin_index = 0
        for dustbin in bins["pos"]:
            bin_pos = self.centerPosition(dustbin, bins["sprite"].tile_size)
            distance = self.getDiagonal(bins["sprite"].tile_size) + self.getDiagonal(trash["sprite"].tile_size)
            if self.distanceBetween(bin_pos, trash_pos) <= distance:
                
                # Checks if it is the right bin
                if trash["index"] // 3 == bin_index:
                    game.right += 1
                else:
                    game.wrong += 1

                trash["falling"] = False
                break
            
            bin_index += 1

        # TODO: Open the bins if trash x is in range

    def distanceBetween(self, posA, posB):
        """Returns the distance between two points"""
        x = posB[0] - posA[0]
        y = posB[1] - posA[1]
        dist = (x ** 2 + y ** 2) ** 0.5
        return dist

    def getDiagonal(self, size):
        """Returns a half diagonal of a square based on width and height"""
        if isinstance(size, tuple):
            w = size[0]
            h = size[1]
        elif isinstance(size, int):
            w = h = size

        return ((w/2) ** 2 + (h/2) ** 2) ** 0.5

    def centerPosition(self, lst, size):
        """Returns the center position of a square based on its top-left corner position"""
        if isinstance(size, tuple):
            w = size[0]
            h = size[1]
        elif isinstance(size, int):
            w = h = size

        return (lst[0] + w / 2, lst[1] + h / 2)
