
import random
from filters import WallFilter, SelfFilter, FoodFilter, EnemyFilter, HeadOnLookAheadFilter, DontWreckYoSelfFilter

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

__author__ = 'awhite'


class Game(object):

    name = None
    snakes = None
    board = None
    turn = None

    def __init__(self, name, turn, snakes, board):
        self.name = name
        self.turn = turn
        self.snakes = snakes
        self.board = board


class Snake(object):

    id = None
    state = None
    coords = None
    health = None
    head = None
    board = None
    turn = None
    health_threshold = None
    left = False

    LEFT = 'west'
    RIGHT = 'east'
    UP = 'north'
    DOWN = 'south'

    directions = None

    def __init__(self, id, state, coords, turn, board, enemies=None, last_eaten=None):
        self.id = id
        self.state = state
        self.board = board
        self.coords = coords
        self.turn = turn
        self.head_x = coords[0][0]
        self.head_y = coords[0][1]

        self.enemies = enemies
        self.last_eaten = last_eaten

        if board:
            self.heath_threshold = board.height / 2
        else:
            self.heath_threshold = 50

        self.directions = [
            self.LEFT,
            self.RIGHT,
            self.UP,
            self.DOWN,
        ]

        logger.info("Head: %s,%s" % (self.head_x, self.head_y))

    @property
    def is_alive(self):
        return self.state == 'alive'

    @property
    def health(self):

        if self.last_eaten:

            health_diff = self.turn - self.last_eaten

            return 100 - health_diff - 1

        return 100 - self.turn - 1

    @property
    def length(self):
        return len(self.coords)

    @property
    def is_biggest(self):

        if self.enemies:

            enemy_lengths = [enemy.length for enemy in self.enemies]

            return self.length > max(enemy_lengths)

        return True

    def move(self):

        allowable_actions = [self.DOWN, self.UP, self.LEFT, self.RIGHT]

        self.filters = []

        self.filters.append(WallFilter())
        self.filters.append(SelfFilter())
        self.filters.append(EnemyFilter())

        if self.health < self.health_threshold or not self.is_biggest:
            self.filters.append(FoodFilter())

        self.filters.append(HeadOnLookAheadFilter())

        # self.filters.append(DontWreckYoSelfFilter())

        for filter in self.filters:
            allowable_actions = filter.apply(self, allowable_actions)

        return random.choice(allowable_actions)

    def __str__(self):
        return '<Snake: %s>' % self.id


class Food(object):
    x = None
    y = None

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, snake_x, snake_y):

        distance = (snake_x - self.x)**2 + (snake_y - self.y)**2

        logger.info("Food %s, %s is %s away", self.x, self.y, distance)

        return distance


class Tile(object):

    state = None
    x = None
    y = None

    STATE_CHOICES = ('head', 'body', 'food', 'empty')

    def __init__(self, state, x, y):

        if state not in self.STATE_CHOICES:
            raise Exception("WTF is this state: %s" % state)

        self.state = state
        self.x = x
        self.y = y


class Board(object):
    height = None
    width = None
    tile_array = None
    tiles = None
    food = None

    def __init__(self, height, width, food):

        self.height = height
        self.width = width

        self.tiles = {}
        self.food = []

        for x in range(width):
            for y in range(height):

                state = 'empty'

                if [x,y] in food:
                    state = 'food'
                    logger.info("Got food tile: %s, %s", x, y)
                    self.food.append(Food(x, y))

                self.tiles[(x, y)] = Tile(state, x, y)


