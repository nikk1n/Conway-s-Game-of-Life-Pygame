import pygame
import sys
import os
import random
from pathlib import Path

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
os.chdir(Path("C:/Users/User/PycharmProjects/Life of Game/Sprites"))
os.getcwd()
pygame.mixer.music.load("background.wav")
pygame.mixer.music.play(-1)
button_click = pygame.mixer.Sound("button.wav")
init_sound = pygame.mixer.Sound("menu.wav")
fps = 60
clock = pygame.time.Clock()
my_font = pygame.font.SysFont('Arial MC', 44)
running = True
living = False
edit = True
main_objects = []
menu_objects = []
mouse_state = 2
last = pygame.time.get_ticks()
now = pygame.time.get_ticks()
interval = 50
pygame.display.set_caption("Conway's Game of Life")
Info = pygame.display.Info()
cell_x_amount = 1
cell_y_amount = 1
m_cell_size = int(min((Info.current_w - 100) / cell_x_amount, (Info.current_h - 100) / cell_y_amount))
X = 1200
Y = 520
screen = pygame.display.set_mode((X, Y))
mode = "menu"


class Cell:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.alive = False
        self.alive_neighbours = 0
        self.colors = {
            "regular": ((230, 230, 250), (0, 0, 0)),
            "hover": ((235, 235, 235), (40, 40, 40))}
        self.cell_surface = pygame.Surface((self.width, self.height))
        self.cell_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.pressed = False
        main_objects.append(self)

    def process(self):
        mouse_pos = pygame.mouse.get_pos()
        self.cell_surface.fill(self.colors["regular"][int(self.alive)])
        if self.cell_rect.collidepoint(mouse_pos):
            self.cell_surface.fill(self.colors["hover"][int(self.alive)])
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                if not self.pressed:
                    global mouse_state
                    if mouse_state == 2:
                        mouse_state = not self.alive
                    self.alive = mouse_state
                    self.pressed = True
        screen.blit(self.cell_surface, self.cell_rect)


class Grid:
    def __init__(self, x, y, width, height, x_cell, y_cell, cell_size):
        self.x = x
        self.y = y
        self.x_cell = x_cell
        self.y_cell = y_cell
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cells = []
        for i in range(0, self.y_cell):
            self.cells.append([])
            for j in range(0, self.x_cell):
                self.cells[len(self.cells) - 1].append(
                    Cell(self.x + j * self.cell_size, self.y + i * self.cell_size, self.cell_size - 1,
                         self.cell_size - 1))

    def neighbours(self):
        for row in range(len(self.cells)):
            for col in range(len(self.cells[row])):
                for i in range(row - 1, row + 2):
                    if i > len(self.cells) - 1 or i < 0:
                        continue
                    for j in range(col - 1, col + 2):
                        if j > len(self.cells[i]) - 1 or j < 0:
                            continue
                        if j == col and i == row:
                            continue
                        if self.cells[i][j].alive == 1:
                            self.cells[row][col].alive_neighbours += 1

    def process(self):
        self.neighbours()
        for row in self.cells:
            for cell in row:
                if (cell.alive_neighbours == 2 and cell.alive) or cell.alive_neighbours == 3:
                    cell.alive = True
                else:
                    cell.alive = False
                cell.alive_neighbours = 0

    def clear(self):
        for row in self.cells:
            for cell in row:
                cell.alive = False

    def mouse_release(self):
        for row in self.cells:
            for cell in row:
                cell.pressed = False

    def randomize(self):
        for row in self.cells:
            for cell in row:
                cell.alive = bool(random.randint(0, 1))


class Button:
    def __init__(self, object_list, x, y, width, height, images, click_function, toggle_img=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.click_function = click_function
        self.pressed = False
        self.images = []
        for img in images:
            img = pygame.image.load(img)
            img = pygame.transform.scale(img, (self.width, self.height))
            self.images.append(img)
        self.button_img = self.images[0]
        self.toggle = False
        if toggle_img is not None:
            self.toggle_images = []
            for img in toggle_img:
                img = pygame.image.load(img)
                img = pygame.transform.scale(img, (self.width, self.height))
                self.toggle_images.append(img)
            self.toggle = True
        self.button_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        object_list.append(self)

    def process(self):
        mouse_pos = pygame.mouse.get_pos()
        self.button_img = self.images[0]
        if self.button_rect.collidepoint(mouse_pos):
            self.button_img = self.images[1]
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.button_img = self.images[2]
                if not self.pressed:
                    self.click_function()
                    self.pressed = True
                    button_click.play()
                    if self.toggle:
                        self.toggle_images, self.images = self.images, self.toggle_images
            else:
                self.pressed = False
        screen.blit(self.button_img, self.button_rect)


class InputBox:

    def __init__(self, object_list, x, y, width, height, placeholder_text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (0, 0, 0)
        self.text = ''
        self.txt_surface = my_font.render(placeholder_text, True, self.color)
        self.active = False
        object_list.append(self)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
                self.text = ''
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = (135, 206, 250) if self.active else (0, 0, 0)
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.unicode.isdigit():
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = my_font.render(self.text, True, (0, 0, 0))

    def process(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)


class TextBox:
    def __init__(self, object_list, x, y, text, color=(0, 0, 0), size=12):
        self.x = x
        self.y = y
        self.text = text
        self.font = pygame.font.SysFont("Arial MC", size)
        self.color = color
        self.txt_surface = self.font.render(self.text, True, self.color)
        object_list.append(self)

    def process(self):
        self.txt_surface = self.font.render(self.text, True, self.color)
        screen.blit(self.txt_surface, (self.x, self.y))


def play():
    global living
    living = not living


def forward():
    g.process()


def back():
    global mode
    global screen
    global X
    global Y
    global living
    living = 0
    X = 1200
    Y = 720
    screen = pygame.display.set_mode((X, Y))
    mode = "menu"


def leave():
    pygame.quit()
    sys.exit()


def start():
    cell_dimensions = []
    for inp in input_boxes:
        if inp.text == '':
            error_box.text = "Please enter the size of the grid"
            return
        cell_dimensions.append(int(inp.text))
    global cell_x_amount
    global cell_y_amount
    global m_cell_size
    global X
    global Y
    global screen
    global mode
    global main_objects
    global g
    cell_x_amount = cell_dimensions[0]
    cell_y_amount = cell_dimensions[1]
    m_cell_size = int(min((Info.current_w - 100) / cell_x_amount, (Info.current_h - 100) / cell_y_amount))
    X = m_cell_size * cell_x_amount
    Y = m_cell_size * cell_y_amount + 40
    screen = pygame.display.set_mode((X, Y))
    main_objects = []
    g = Grid(0, 40, X, Y, cell_x_amount, cell_y_amount, m_cell_size)
    Button(main_objects, 50, 5, 30, 30, ("play_reg.png", "play_hover.png", "play_press.png"), play,
           ("pause_reg.png", "pause_hover.png", "pause_press.png"))
    Button(main_objects, 90, 5, 30, 30, ("forward_reg.png", "forward_hover.png", "forward_press.png"), forward)
    Button(main_objects, 130, 5, 30, 30, ("clear_reg.png", "clear_hover.png", "clear_press.png"), g.clear)
    Button(main_objects, 170, 5, 30, 30, ("random_reg.png", "random_hover.png", "random_press.png"), g.randomize)
    Button(main_objects, X - 90, 5, 30, 30, ("back_reg.png", "back_hover.png", "back_press.png"), back)
    Button(main_objects, X - 50, 5, 30, 30, ("quit_reg.png", "quit_hover.png", "quit_press.png"), leave)
    init_sound.play()
    mode = "main"
    pygame.time.delay(100)


g = Grid(0, 0, 0, 0, 1, 1, 1)
inp_box_w = InputBox(menu_objects, X / 3.7, Y / 1.5, 100, 44, "x (in cells)")
inp_box_h = InputBox(menu_objects, X / 1.7, Y / 1.5, 100, 44, "y (in cells)")
input_boxes = [inp_box_w, inp_box_h]
error_box = TextBox(menu_objects, X // 2 - 100, Y - 25, "", (220, 20, 60), 24)
rules = (
    "The universe of the Game of Life is a grid of square cells, each of which can be either dead(white) or alive("
    "black).\n"
    "Every cell interacts with its 8 neighbors(adjacent cells). At each step in time:\n 1) Any live cell with less "
    "than 2 neighbours dies \n 2) Any live cell with 2 or 3 neighbours lives \n 3) Any live cell with 4 or more "
    "neighbours dies \n 4) Dead cells with exactly 3 neighbours become alive.\nThe initial pattern - seed of the system"
    " can be randomly generated or drawn manually using left mouse button.")
mar = 3
for line in rules.split('\n'):
    TextBox(menu_objects, 2, mar, line, (0, 0, 0), 32)
    mar += 30
TextBox(menu_objects, 2, Y / 1.9, "Before starting you need to choose the size of your x by y grid:", size=32)
Button(menu_objects, X // 2 - 125, Y - 150, 300, 150, ("start_reg.png", "start_hover.png", "start_press.png"), start)
while running:
    if mode == "main":
        screen.fill((200, 200, 200))
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, X, 40))
        pygame.draw.rect(screen, (224, 224, 224), (2, 2, X - 4, 36))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_state = 2
                edit = True
                g.mouse_release()
            if event.type == pygame.MOUSEBUTTONDOWN:
                edit = False
        for some_object in main_objects:
            some_object.process()
        if living and edit:
            now = pygame.time.get_ticks()
            if now - last >= interval:
                g.process()
                last = now
    elif mode == "menu":
        screen.fill((230, 230, 250))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for box in input_boxes:
                box.handle_event(event)
        for some_object in menu_objects:
            some_object.process()
    pygame.display.flip()
    clock.tick(fps)
