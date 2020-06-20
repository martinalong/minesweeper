import random
import pygame

#num_mines, width, height
EASY =  [10, 10, 8]
MEDIUM = [40, 18, 14]
HARD = [99, 24, 20]

LEFT = 1
RIGHT = 3

SCREEN_WIDTH = 550
SCREEN_HEIGHT = 440

TILE_SIZE = 20

#easy medium hard selection
#reset game button
#reveals all the mines that were hidden after if you hit a mine, and x-es all the flags that were wrong
#you win you lose at top

#if first click is a mine, move that mine to another prespecified random place (the next one in the array)

#decremeent the value for the ai if there's a marked mine in the vicinity 

#setup window
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Minesweeper")

#load images
background = pygame.image.load('background.png')
background = pygame.image.load('background.png')
background = pygame.image.load('background.png')

class Board(object):
    """ A 17 x 11 board """
    board = []
    status = "play" #play, win, lose

    def __init__(self, difficulty):
        """ Creates a board of Place objects and fills them with the initial stones and bricks """
        self.mines = difficulty[0] #may be able to use same for flags and mines, unless need to access mine number later on
        self.flags = difficulty[0]
        self.width = difficulty[1]
        self.height = difficulty[2]
        self.remaining = self.width * self.height - self.mines #win when it's 0
        Board.x_offset = (SCREEN_WIDTH - self.width * TILE_SIZE) / 2.0  #just 2 should with python3
        Board.y_offset = (SCREEN_HEIGHT - self.height * TILE_SIZE) / 2.0
        Board.board = [[Place(x, y) for x in range(self.width)] for y in range(self.height)]
        spaces_arr = random.shuffle(range(self.width * self.height))
        for i in range(self.mines):
            spot = spaces_arr[i]
            y = spot // self.width
            x = spot % self.width
            place = Board.board[y][x]
            place.add_mine()
            for x_pos in range(max(0,x-1), min(self.width,x+2)):
                for y_pox in range(max(0,y-1), min(self.height, y+2)):
                    Board.board[y_pos][x_pos].increment()
        self.backup_space = spaces_arr[self.width * self.height]

    def move_mine(self, x, y):
        """ If clicks on mine the first move, relocates mine to next spot in the array """
        Board.board[y][x].remove_mine()
        Board.board[self.backup_space // self.width][self.backup_space % self.width].add_mine()

    def register_click(self, click, x_pos, y_pos):
        """ Registers a click on the given coordinates and executes accordingly """
        x = (x_pos - x_offset) // TILE_SIZE
        y = (y_pos - y_offset) // TILE_SIZE
        if click == "right":
            self.flags -= board[y][x].flag()
        elif click == "left":
            if not board[y][x].show:
                if board[y][x].mine:
                    board[y][x].show()
                    Board.status = "lose"
                else:
                    self.clear_surround(x, y)

    def clear_surround(self, x, y):
        """ Clear all surrounding tiles up to border of tiles that are numbered or up to already revealed tiles. """
        if x < 0 or y < 0 or x >= self.width or y >= self.height or Board.status == "win":
            return
        tile = Board.board[y][x]
        if tile.show:
            return
        self.remaining -= tile.show()
        if self.remaining == 0:
            Board.status = "win"
        if not tile.count:
            self.clear_surround(x-1, y)
            self.clear_surround(x+1, y)
            self.clear_surround(x, y-1)
            self.clear_surround(x, y+1)

    def show_all(self):
        """ Reveal all unshown tiles and x out any incorrectly flagged tiles """
        for x in self.width:
            for y in self.height:
                tile = Board.board[y][x]
                if not tile.show:
                    if tile.flag and tile.mine:
                        #x
                    elif tile.mine:
                        #mine
                    elif tile.count:
                        #count
                    else:
                        #blank

class Place(object):
    """ A spot on the board with x and y coordinates and potentially a mine, which stores state (unclicked, clicked, flagged) """
    def __init__(self, x, y):
        self.mine = False
        self.show = False
        self.flag = False
        self.count = 0
        self.x = x
        self.y = y
        self.pos = (Board.x_offset + x_pos * TILE_SIZE, Board.y_offset + y_pos * TILE_SIZE)

    def add_mine(self):
        """ Add mine. Only called during setup or to relocate mine hit on first click """
        self.mine = True

    def remove_mine(self):
        """ Remove mine. Only called to relocate mine hit on first click """
        self.mine = False

    def increment(self):
        """ Increments the count for number of nearby mines """
        self.count += 1

    def show(self):
        """ Reveals a tile. Does nothing if flagged or already revealed. Returns 1 if a tile is revealed, 0 if not """
        if (not self.flag and not self.show):
            self.show = True
            if self.mine:
                #blit red mine
            elif self.count:
                #blit count
            else:
                #blit blank
            return 1
        return 0

    def flag(self):
        """ Flags/unflags a tile. Does nothing if already shown. Returns if flag added (+1) or subtracted(-1) """
        if (not self.show):
            self.flag = not self.flag
            if self.flag:
                #blit flag
                return 1
            else:
                #blit unclicked
                return -1
        return 0
        

###############################################
############### GAME OPERATIONS ###############
###############################################
    

#game setup
screen.blit(background, (0, 0))

screen.blit()
pygame.display.update()

#game loop
running = True
while running:
    setup = True
    difficulty = EASY
    while setup:
        if event.type == pygame.QUIT:
            running = False
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    difficulty = EASY
                    setup = False
                elif event.key == pygame.K_m:
                    difficulty = MEDIUM
                    setup = False
                elif event.key = pygame.K_h:
                    difficulty = HARD
                    setup = False
    board = Board(difficulty)    
    #display board.flags at the top
    while board.status == "play":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == LEFT:
                        #left click
                    if event.button == RIGHT:
                        #right click
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                        print "You pressed the left mouse button at (%d, %d)" % event.pos
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        p1.change = up
                        p1.img = red_up
                    elif event.key == pygame.K_DOWN:
                        p1.change = down
                        p1.img = red_down
                    elif event.key == pygame.K_LEFT:
                        p1.change = left
                        p1.img = red_left
                    elif event.key == pygame.K_RIGHT:
                        p1.change = right
                        p1.img = red_right
                    elif event.key == pygame.K_SPACE:
                        p1.drop_balloon()
                    if event.key == pygame.K_w:
                        p2.change = up
                        p2.img = white_up
                    elif event.key == pygame.K_s:
                        p2.change = down
                        p2.img = white_down
                    elif event.key == pygame.K_a:
                        p2.change = left
                        p2.img = white_left
                    elif event.key == pygame.K_d:
                        p2.change = right
                        p2.img = white_right
                    elif event.key == pygame.K_z:
                        p2.drop_balloon()   
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        if p1.change == up:
                            p1.change = stay
                    elif event.key == pygame.K_DOWN:
                        if p1.change == down:
                            p1.change = stay
                    elif event.key == pygame.K_LEFT:
                        if p1.change == left:
                            p1.change = stay
                    elif event.key == pygame.K_RIGHT:
                        if p1.change == right:
                            p1.change = stay
                    if event.key == pygame.K_w:
                        if p2.change == up:
                            p2.change = stay
                    elif event.key == pygame.K_s:
                        if p2.change == down:
                            p2.change = stay
                    elif event.key == pygame.K_a:
                        if p2.change == left:
                            p2.change = stay
                    elif event.key == pygame.K_d:
                        if p2.change == right:
                            p2.change = stay
        p1.move()
        p2.move()
        for tup in board.places:
            p = board.board[tup[0]][tup[1]] 
            if p.obj:
                screen.blit(p.obj.img, p.pos)
                if isinstance(p.obj, Balloon):
                    p.obj.tick()
            elif p.powerup:
                screen.blit(p.powerup.img, p.pos)
            if p.monkey:
                screen.blit(p.monkey.img, p.monkey.pos)
                if p.monkey.bubble:
                    screen.blit(bubble, p.monkey.pos)
                    p.monkey.tick()
            if p.splash: 
                screen.blit(p.splash.img, p.pos)
                p.splash.tick()
        pygame.display.update()
    pygame.quit()