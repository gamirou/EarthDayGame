import pygame, pygame.locals
import time, math

from enum import Enum
from string import printable

class MenuStates(Enum):
    """Where we can be in the menu system."""
    PLAY = 0,
    MAIN_MENU = 1,
    CHAR_SETUP = 2,
    HELP = 4,
    QUIT = 5


class MenuState:
    def __init__(self, framework):
        self.framework = framework
        self.screen = framework.screen
        self.current_state = MenuStates.MAIN_MENU
        self.font_path = 'assets/fonts/nyala.ttf'

        self.fonts = {
            'small': pygame.font.Font(self.font_path, 35),
            'normal': pygame.font.Font(self.font_path, 55),
            'large': pygame.font.Font(self.font_path, 75),
            'heading': pygame.font.Font(self.font_path, 95),
        }

        self.structure = {
            MenuStates.MAIN_MENU: MenuItem(self, {
                "Play": MenuStates.CHAR_SETUP,
                "Help": MenuStates.HELP,
                "Quit": MenuStates.QUIT
            }),
            MenuStates.CHAR_SETUP: CharSetupMenuItem(self, {
                "Name": None,
                "Gender": None,
                "Start Game": None,
                "Back": MenuStates.MAIN_MENU,
            }),
            MenuStates.HELP: HelpMenuItem(self, {
                "Back": MenuStates.MAIN_MENU
            }),
            MenuStates.PLAY: None,
            MenuStates.QUIT: None,
        }

    def get_current(self):
        return self.structure[self.current_state]

    def get_screen_data(self, state: MenuStates):
        return self.structure[state]

    def update(self, dt: float, events: list):
        if self.current_state == MenuStates.PLAY:
            char_data = self.get_screen_data(MenuStates.CHAR_SETUP)
            self.framework.enter_game(char_data.char_name, char_data.gender_options[char_data.gender_choice])
            return
        elif self.current_state == MenuStates.QUIT:
            pygame.event.post(pygame.event.Event(pygame.QUIT, {}))

        if self.get_current():
            self.get_current().render()
            self.get_current().update(dt, events)

class MenuItem:
    def __init__(self, menu_state: MenuState, options={}):
        self.menu_state = menu_state
        self.screen = menu_state.screen

        self.options = options
        self.options_shift = (55, 55)
        self.selected_option = 0

        self.font = self.menu_state.fonts['normal']
        self.info_font = self.menu_state.fonts['small']
        self.header_font = self.menu_state.fonts['heading']

        self.logosurf = pygame.image.load('assets/images/logo.fw.png')

    def update(self, dt, events) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.locals.K_UP:
                    self.selected_option -= 1
                    self.selected_option %= len(self.options)
                elif event.key == pygame.locals.K_DOWN:
                    self.selected_option += 1
                    self.selected_option %= len(self.options)
                elif event.key == pygame.locals.K_RETURN:
                    option_values = list(self.options.values())
                    self.menu_state.current_state = option_values[self.selected_option] or MenuStates.MAIN_MENU

    def get_screen_centre(self):
        return pygame.Vector2(
            self.menu_state.framework.dimensions[0] / 2,
            self.menu_state.framework.dimensions[1] / 2
        )

    def aspect_scale(self,img,bx,by):
        """ Scales 'img' to fit into box bx/by.
        This method will retain the original image's aspect ratio """
        ix,iy = img.get_size()
        if ix > iy:
            # fit to width
            scale_factor = bx/float(ix)
            sy = scale_factor * iy
            if sy > by:
                scale_factor = by/float(iy)
                sx = scale_factor * ix
                sy = by
            else:
                sx = bx
        else:
            # fit to height
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            if sx > bx:
                scale_factor = bx/float(ix)
                sx = bx
                sy = scale_factor * iy
            else:
                sy = by

        return pygame.transform.smoothscale(img, (int(sx),int(sy)))

    def render(self) -> None:
        self.render_options(self.font, (
            self.get_screen_centre()[0] - self.options_shift[0],
            self.get_screen_centre()[1] - self.options_shift[1]
        ))
        logo = self.aspect_scale(self.logosurf,int(self.screen.get_rect().width/2),self.screen.get_rect().height)
        self.screen.blit(logo,(self.screen.get_rect().width/2 - logo.get_rect().width/2,self.screen.get_rect().height/4 - logo.get_rect().height/2))


    def render_text(self, font, text, pos=(0, 0), colour=(255, 255, 255)):
        rendered_text_surface = font.render(text, False, colour)
        self.screen.blit(rendered_text_surface, pos)

    def render_options(self, font, offset=(0, 0)):
        for index, value in enumerate(self.options.keys()):
            text = value
            if index == self.selected_option:
                text = "> {0}".format(text)

            self.render_text(font, text, (index + offset[0], index * 55 + offset[1]))


class CharSetupMenuItem(MenuItem):
    def __init__(self, menu_state, options={}):
        super().__init__(menu_state, options)
        self.options_shift = (100, -200)
        self.char_name = ""
        self.ticker = 0
        self.char_name_max = 15
        self.gender_options = ("Boy", "Girl")
        self.gender_choice = 0

    def update(self, dt, events) -> None:
        """Update values for the character setup menu page"""
        option_values = list(self.options.values())
        option_keys = list(self.options.keys())
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.locals.K_UP:
                    self.selected_option -= 1
                    self.selected_option %= len(self.options)
                elif event.key == pygame.locals.K_DOWN:
                    self.selected_option += 1
                    self.selected_option %= len(self.options)
                elif event.key == pygame.locals.K_RETURN:
                    if option_values[self.selected_option] is not None:
                        self.menu_state.current_state = option_values[self.selected_option] or MenuStates.MAIN_MENU
                    elif option_keys[self.selected_option] == "Start Game":
                        if len(self.char_name) != 0:
                            self.menu_state.current_state = MenuStates.PLAY
                elif option_keys[self.selected_option] == "Name":
                    if event.key == pygame.locals.K_BACKSPACE:
                        self.char_name = self.char_name[:-1]
                    elif event.key < 123 and event.key != 13 and len(self.char_name) < self.char_name_max:
                        char_new = chr(event.key)
                        if char_new in printable:
                            if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                                self.char_name += char_new.upper()
                            else:
                                self.char_name += char_new
                elif option_keys[self.selected_option] == "Gender":
                    if event.key == pygame.locals.K_RIGHT:
                        self.gender_choice += 1
                    elif event.key == pygame.locals.K_LEFT:
                        self.gender_choice -= 1

            self.gender_choice %= len(self.gender_options)

        self.ticker += 2
        self.ticker %= 100

    def render(self) -> None:
        font = self.font
        offset = self.get_screen_centre() + (-150, 100)

        name_string = '> Name:' if self.selected_option == 0 else 'Name:'
        self.render_text(self.font, name_string, self.get_screen_centre() - (150, 50))
        if self.ticker > 50 and self.selected_option == 0:
            self.render_text(self.font, self.char_name + "_", self.get_screen_centre() - (-20, 50))
        else:
            self.render_text(self.font, self.char_name, self.get_screen_centre() - (-20, 50))

        gender_string = '>' if self.selected_option == 1 else ''
        self.render_text(self.font, 'Are you a:', self.get_screen_centre() - (150, 10))
        self.render_text(self.font, gender_string, self.get_screen_centre() - (150, -40))
        self.render_text(self.font, " " + self.gender_options[self.gender_choice], self.get_screen_centre() - (130, -40))


        for index, value in enumerate(self.options.keys()):
            if self.options[value] is None and value != "Start Game":
                continue

            text = value
            if index == self.selected_option:
                text = "> {0}".format(text)

            self.render_text(font, text, (index + offset[0], index * 55 + offset[1]))
        logo = self.aspect_scale(self.logosurf,int(self.screen.get_rect().width/2),self.screen.get_rect().height)
        self.screen.blit(logo,(self.screen.get_rect().width/2 - logo.get_rect().width/2,self.screen.get_rect().height/4 - logo.get_rect().height/2))


class HelpMenuItem(MenuItem):
    def __init__(self, menu_state, options={}):
        super().__init__(menu_state, options)

    def update(self, dt, events) -> None:
        super().update(dt, events)

    def render(self) -> None:
        super().render()
