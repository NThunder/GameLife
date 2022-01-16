import pygame
import pygame.locals
from random import randint
import sys


class Cell:
    def __init__(self, state=0):
        self.state = state
        self.new_state = state


class Grid:

    def __init__(self, width, height, rand=0):
        self.grid_width = width
        self.grid_height = height
        if rand:
            self.grid = [[Cell(randint(0, 1)) for w in range(self.grid_width)] for h in range(self.grid_height)]
        else:
            self.grid = [[Cell(0) for w in range(self.grid_width)] for h in range(self.grid_height)]

    def get_neighbours(self, cell_h, cell_w):
        cells = []
        for dh in range(-1, 2):
            for dw in range(-1, 2):
                height = cell_h + dh
                width = cell_w + dw
                if height != cell_h or width != cell_w:
                    if 0 <= height < self.grid_height and 0 <= width < self.grid_width:
                        cells.append(self.grid[height][width])
        return cells

    def get_next_generation(self) -> bool:
        instab = False
        for height in range(self.grid_height):
            for width in range(self.grid_width):
                neighbor_cells = self.get_neighbours(height, width)
                living_cells = 0
                for cell in neighbor_cells:
                    living_cells += cell.state
                if self.grid[height][width].state == 0 and living_cells == 3:
                    self.grid[height][width].new_state = 1
                    instab = True
                elif living_cells != 3 and living_cells != 2 and self.grid[height][width].state == 1:
                    self.grid[height][width].new_state = 0
                    instab = True
        return instab

    def clear_grid(self):
        self.grid = [[Cell() for w in range(self.grid_width)] for h in range(self.grid_height)]

    def random_grid(self):
        self.grid = [[Cell(randint(0, 1)) for w in range(self.grid_width)] for h in range(self.grid_height)]


class GameLife(Grid):

    def __init__(self, width=640, height=480, cell_size=10, speed=1, rand=0):
        super().__init__(width // cell_size, height // cell_size, rand)
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.screen_size = width, height
        self.screen = pygame.display.set_mode(self.screen_size)
        self.speed = speed

    def draw_lines(self):
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color("black"), (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color("black"), (0, y), (self.width, y))

    def draw_grid(self) -> bool:
        instab = False
        if self.get_next_generation():
            instab = True
        for height in range(self.grid_height):
            for width in range(self.grid_width):
                rect = width * self.cell_size, height * self.cell_size, self.cell_size, self.cell_size
                if self.grid[height][width].new_state == 1:
                    pygame.draw.rect(self.screen, pygame.Color('green'), rect)
                else:
                    pygame.draw.rect(self.screen, pygame.Color('white'), rect)
                self.grid[height][width].state = self.grid[height][width].new_state
        return instab

    def display_cell(self, h_pos, w_pos, cleaning):
        rect = w_pos * self.cell_size, h_pos * self.cell_size, self.cell_size, self.cell_size
        if self.grid[h_pos][w_pos].state == 1 and cleaning:
            pygame.draw.rect(self.screen, pygame.Color('white'), rect)
            self.grid[h_pos][w_pos].state = self.grid[h_pos][w_pos].new_state = 0
        elif self.grid[h_pos][w_pos].state == 0 and cleaning == 0:
            pygame.draw.rect(self.screen, pygame.Color('green'), rect)
            self.grid[h_pos][w_pos].state = self.grid[h_pos][w_pos].new_state = 1
        self.draw_lines()
        pygame.display.update()

    def start(self):
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption("Game Life")
        self.screen.fill(pygame.Color("white"))
        self.draw_lines()
        pygame.display.update()
        drawing, running, pause, h_pos, w_pos, cleaning = 0, True, 1, 0, 0, 0
        while running:
            for event in pygame.event.get():
                if event.type == pygame.locals.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    pause = 1 - pause
                    drawing = 0
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and pause:
                    drawing = 1
                    w_pos = event.pos[0] // self.cell_size
                    h_pos = event.pos[1] // self.cell_size
                    if self.grid[h_pos][w_pos].state == 1:
                        cleaning = 1
                    else:
                        cleaning = 0
                    self.display_cell(h_pos, w_pos, cleaning)
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and pause:
                    drawing = 0
                if event.type == pygame.MOUSEMOTION and drawing:
                    new_w_pos = event.pos[0] // self.cell_size
                    new_h_pos = event.pos[1] // self.cell_size
                    if new_h_pos != h_pos or new_w_pos != w_pos:
                        self.display_cell(new_h_pos, new_w_pos, cleaning)
                        h_pos = new_h_pos
                        w_pos = new_w_pos
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE):
                    self.clear_grid()
                    pause = 0
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.random_grid()
                    pause = 0
                if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                    if self.speed > 1:
                        self.speed -= 1
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                    self.speed += 1
                if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                    if self.cell_size > 10:
                        self.cell_size -= 10
                        pause = 0

                if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                    self.cell_size += 10
                    pause = 0

            if not pause:
                if not self.draw_grid():
                    pause = 1
                self.draw_lines()
                pygame.display.flip()
                clock.tick(self.speed)
        pygame.quit()


if __name__ == '__main__':
    args = [int(i) for i in sys.argv[1:]]
    game = GameLife(*args)
    game.start()
