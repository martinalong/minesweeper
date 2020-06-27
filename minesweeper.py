import random
import pygame
from pygame.locals import *

#num_mines, width, height
EASY =  [10, 10, 8]
MEDIUM = [40, 18, 14]
HARD = [99, 24, 20]

LEFT = 1
RIGHT = 3

SCREEN_WIDTH = 750
SCREEN_HEIGHT = 690
TOP_BAR = 20

TILE_SIZE = 30

#setup window
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Minesweeper")

alarm_font = pygame.font.Font('alarm_clock.ttf', 40) 
roboto_font = pygame.font.Font('Roboto-Regular.ttf', 30)
RED = (255, 0, 0) 
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

#load images
background = pygame.transform.scale(pygame.image.load('background.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT))
mine = pygame.image.load('mine.png')
red_mine = pygame.image.load('red_mine.png')
x_mine = pygame.image.load('x_mine.png')
flag = pygame.image.load('flag.png')
block = pygame.image.load('block.png')
numbers = [pygame.image.load('empty.png')]
for i in range(1, 9):
    numbers.append(pygame.image.load('%dtile.png' % (i)))
    

class Game(object):
    """ A minesweeper game with a board represented by a 2D array of Place objects """
    def __init__(self, difficulty):
        """ Creates a board of Place objects and fills them with the initial stones and bricks """
        self.mines = difficulty[0] #may be able to use same for flags and mines, unless need to access mine number later on
        self.flags = difficulty[0]
        self.width = difficulty[1]
        self.height = difficulty[2]
        self.remaining = self.width * self.height - self.mines #win when it's 0
        self.x_offset = int((SCREEN_WIDTH - self.width * TILE_SIZE) / 2.0)  #just 2 should with python3
        self.y_offset = int((SCREEN_HEIGHT - self.height * TILE_SIZE) / 2.0 + TOP_BAR)
        self.board = [[Place(x, y, self) for x in range(self.width)] for y in range(self.height)]
        self.status = "play"
        self.first = True

    def get_coord(self, x_pos, y_pos):
        """ Get the x, y board coordinate that corresponds to a x_pos and y_pos position on the screen """
        x = (x_pos - self.x_offset) // TILE_SIZE
        y = (y_pos - self.y_offset) // TILE_SIZE
        return x, y

    def set_mines(self, x_init, y_init):
        """ (x, y) is the coordinate of the first click. Makes sure there are no mines there or in the immediate vicinity """
        spaces_arr = list(range(self.width * self.height))
        random.shuffle(spaces_arr)
        for x_pos in range(max(0, x_init - 1), min(self.width, x_init + 2)):
            for y_pos in range(max(0, y_init - 1), min(self.height, y_init + 2)):
                spaces_arr.remove(y_pos * self.width + x_pos)
        for i in range(self.mines):
            spot = spaces_arr[i]
            y = spot // self.width
            x = spot % self.width
            place = self.board[y][x]
            place.add_mine()
            for x_pos in range(max(0,x-1), min(self.width,x+2)):
                for y_pos in range(max(0,y-1), min(self.height, y+2)):
                    self.board[y_pos][x_pos].increment()

    def click_block(self, click, x, y):
        """ Left or right clicks the block at (x, y) """
        tile = self.board[y][x]
        if click == "right":
            self.flags -= tile.flag_tile()
        elif click == "left":
            if not tile.show and not tile.flag:
                if tile.mine:
                    tile.show_tile()
                    self.status = "lose"
                else:
                    self.clear_surround(x, y)

    def register_click(self, click, x_pos, y_pos):
        """ Registers a click on the given screen position and calls click_block on the corresponding block """
        x, y = self.get_coord(x_pos, y_pos)
        self.click_block(click, x, y)

    def clear_surround(self, x, y):
        """ Clear all surrounding tiles up to border of tiles that are numbered or up to already revealed tiles. """
        if x < 0 or y < 0 or x >= self.width or y >= self.height or self.status == "win":
            return
        tile = self.board[y][x]
        if tile.show:
            return
        self.remaining -= tile.show_tile()
        if self.remaining == 0:
            self.status = "win"
        if not tile.count:
            for x_pos in range(max(0, x - 1), min(self.width, x + 2)):
                for y_pos in range(max(0, y - 1), min(self.height, y + 2)):
                    if x_pos != x or y_pos != y:
                        self.clear_surround(x_pos, y_pos)

    def show_all(self):
        """ Reveal all unshown tiles and x out any incorrectly flagged tiles """
        for x in range(self.width):
            for y in range(self.height):
                tile = self.board[y][x]
                if not tile.show:
                    if tile.flag and not tile.mine:
                        screen.blit(x_mine, tile.pos)
                    elif tile.mine:
                        screen.blit(mine, tile.pos)
                    else:
                        screen.blit(numbers[tile.count], tile.pos)

    def tile(self, x, y):
        """ Returns the visible tile at that spot. For use by the robot """
        place = self.board[y][x]
        if place.flag: 
            return "f"
        elif place.show:
            return place.count
        else:
            return "u"


class Place(object):
    """ A spot on the board with x and y coordinates and potentially a mine, which stores state (unclicked, clicked, flagged) """
    def __init__(self, x, y, game):
        self.mine = False
        self.show = False
        self.flag = False
        self.count = 0
        self.x = x
        self.y = y
        self.game = game
        self.pos = (game.x_offset + x * TILE_SIZE, game.y_offset + y * TILE_SIZE)
        screen.blit(block, self.pos)

    def add_mine(self):
        """ Add mine. Only called during setup """
        self.mine = True

    def increment(self):
        """ Increments the count for number of nearby mines """
        self.count += 1

    def show_tile(self):
        """ Reveals a tile. Does nothing if flagged or already revealed. Returns 1 if a tile is revealed, 0 if not """
        if (not self.flag and not self.show):
            self.show = True
            if self.mine:
                screen.blit(red_mine, self.pos)
            else:
                screen.blit(numbers[self.count], self.pos)
            return 1
        return 0

    def flag_tile(self):
        """ Flags/unflags a tile. Does nothing if already shown. Returns if flag added (+1) or subtracted(-1) """
        if (not self.show):
            self.flag = not self.flag
            if self.flag:
                screen.blit(flag, self.pos)
                return 1
            else:
                screen.blit(block, self.pos)
                return -1
        return 0


class Robot(object):
    """ An AI that plays the game of minesweeper 
    Rules:
        1. First move is in the center of the board
        2. Focus on "edge" pieces first
        3. If a piece's true count is 0, that means all remaining around it can be cleared
        4. If a piece's true count is equal to the number of unclicked pieces surrounding it, all those must be mines
        5. If it has to guess, it guesses an unclicked edge piece that is near "lower count" tiles *
        6. Starts searching near the last searched first (optimization) *
        7. Employs "plotting out" strategies where it considers possible orientations of mines in an area given remaining mines (endgame tactic) *
        8. Calculate win proportions across many games *
    """
    def __init__(self, game):
        """ Legend: uncleared = "u", flagged = "f", count = 0, 1, 2... """
        self.game = game
        self.width = game.width
        self.height = game.height

    def tick(self):
        """ A function called every round that causes the robot to make a move (flag or click). """
        if self.game.first:
            self.game.set_mines(self.width // 2, self.height // 2)
            self.clear(self.width // 2, self.height // 2)
            self.game.first = False
        else:
            for i in range(self.width):
                for j in range(self.height):
                    if self.is_edge(i, j):
                        u, f, c = self.count(i, j)
                        if u == c - f:
                            self.flag_surround(i, j)
                            return
                        elif c - f == 0:
                            self.clear_surround(i, j)
                            return
                        
    def is_edge(self, x, y):
        """ Checks if a tile is an edge piece (a non-zero count piece next to unclicked) """
        if not isinstance(self.game.tile(x, y), int) or self.game.tile(x, y) == 0:
            return False
        for i in range(max(0, x-1), min(x+2, self.width)):
            for j in range(max(0, y-1), min(y+2, self.height)):
                if i == x and j == y:
                    continue
                elif self.game.tile(i, j) == "u":
                    return True
        return False    

    def guess(self):
        """ Guesses the unclicked edge piece that is surrounded by the lowest numbers. Calculated as (total surrounding count) / (number surrounding clicked). """

    def count(self, x, y):
        """ Returns 
        1. The number unclicked around it
        2. The number of flags around it
        3. The count of a square """
        count = self.game.tile(x, y)
        u, f = 0, 0
        for i in range(max(0, x-1), min(x+2, self.width)):
            for j in range(max(0, y-1), min(y+2, self.height)):
                if self.game.tile(i, j) == "f":
                    f += 1
                elif self.game.tile(i, j) == "u":
                    u += 1
        return u, f, count

    def flag(self, x, y):
        """ Flags a square """
        if self.game.tile(x, y) == "u":
            self.game.click_block("right", x, y)

    def clear(self, x, y):
        """ Clicks a square """
        if self.game.tile(x, y) == "u":
            self.game.click_block("left", x, y)
    
    def clear_surround(self, x, y):
        """ Clears the surrounding squares """
        for i in range(max(0, x-1), min(x+2, self.width)):
            for j in range(max(0, y-1), min(y+2, self.height)):
                if i == x and j == y:
                    continue
                self.clear(i, j)

    def flag_surround(self, x, y):
        """ Flags the surrounding squares """
        for i in range(max(0, x-1), min(x+2, self.width)):
            for j in range(max(0, y-1), min(y+2, self.height)):
                if i == x and j == y:
                    continue
                self.flag(i, j)
        

###############################################
############### GAME OPERATIONS ###############
###############################################

select_status = "Use keyboard to select difficulty level:" 
select_text = roboto_font.render(select_status, True, WHITE, BLACK)
select_textRect = select_text.get_rect() 
select_textRect.center = (int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 2 - 30))
options_status = "E = easy   M = medium   H = hard"
options_text = roboto_font.render(options_status, True, WHITE, BLACK)
options_textRect = options_text.get_rect() 
options_textRect.center = (int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 2 + 20))

def setup():
    play = True
    while play:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            elif event.type == KEYDOWN:
                if event.key == K_e:
                    return EASY
                elif event.key == K_m:
                    return MEDIUM
                elif event.key == K_h:
                    return HARD

def play_game():
    while True:
        screen.blit(background, (0, 0))
        screen.blit(select_text, select_textRect) 
        screen.blit(options_text, options_textRect) 
        pygame.display.update()
        difficulty = setup()
        screen.blit(background, (0, 0))
        game = Game(difficulty)
        bot = Robot(game)
        text = roboto_font.render("Press space for a hint", True, WHITE, BLUE)
        textRect = text.get_rect() 
        textRect.center = (180,20)
        screen.blit(text, textRect) 
        while game.status == "play":
            pygame.draw.rect(screen, BLACK, [int(SCREEN_WIDTH/2 - 30), int((game.y_offset + 20) // 2 - 25), 60, 50])
            text = alarm_font.render(str(game.flags), True, RED, BLACK)
            textRect = text.get_rect() 
            textRect.center = (int(SCREEN_WIDTH / 2), int((game.y_offset + 20) / 2))
            screen.blit(text, textRect) 
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == LEFT:
                        if game.first:
                            game.set_mines(game.get_coord(event.pos[0], event.pos[1]))
                            game.first = False
                        game.register_click("left", event.pos[0], event.pos[1])
                    if event.button == RIGHT:
                        game.register_click("right", event.pos[0], event.pos[1])
                elif event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        bot.tick()
            pygame.display.update()
        if game.status == "win":
            status = "You win! Click anywhere to restart"
        else:
            game.show_all()
            status = "You lost. Click anywhere to restart"
        text = roboto_font.render(status, True, WHITE, BLACK)
        textRect = text.get_rect() 
        textRect.center = (int(SCREEN_WIDTH / 2), 20)
        screen.blit(text, textRect) 
        pygame.display.update()
        replay = False
        while not replay:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == MOUSEBUTTONDOWN:
                    replay = True
play_game()
pygame.quit()