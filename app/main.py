import os
import bottle
import random
import logging

from models import Snake, Board, Game, Food, Tile

SNAKE_NAME = '2bd68576-4acb-4e9f-b6fd-002975ef3398'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

HEAD_IMG = 'http://www.zoom-comics.com/wp-content/uploads/sites/36/2011/12/pinky-pie-pony.jpg'

TAUNTS = [
    "We're no strangers to love",
    "You know the rules and so do I",
    "A full commitment's what I'm thinking of",
    "You wouldn't get this from any other guy",
    "I just wanna tell you how I'm feeling",
    "Gotta make you understand",
    "We've known each other for so long",
    "Your heart's been aching, but",
    "You're too shy to say it",
    "Inside, we both know what's been going on",
    "We know the game and we're gonna play it",
    "And if you ask me how I'm feeling",
    "Don't tell me you're too blind to see",
    "Never gonna give, never gonna give",
    "Never gonna give, never gonna give",
    "We've known each other for so long",
    "Your heart's been aching, but",
    "You're too shy to say it",
    "Inside, we both know what's been going on",
    "We know the game and we're gonna play it",
    "I just wanna tell you how I'm feeling",
    "Gotta make you understand",
    "Never gonna give you up",
    "Never gonna let you down",
    "Never gonna run around and desert you",
    "Never gonna make you cry",
    "Never gonna say goodbye",
    "Never gonna tell a lie and hurt you",
]


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.get('/')
def index():


    return {
        'name': SNAKE_NAME,
        'color': '#ff69b4',
        'head_url': HEAD_IMG,
        'taunt': random.choice(TAUNTS)
    }


@bottle.post('/start')
def start():
    data = bottle.request.json

    # TODO: Do things with data

    return {
        'taunt': random.choice(TAUNTS)
    }


@bottle.post('/move')
def move():
    data = bottle.request.json


    turn = data['turn']
    snakes = data['snakes']

    # game = Game(name, turn, snakes, board_data)
    height = data['height']
    width = data['width']
    food = data['food']

    board = Board(height, width, food)

    # logger.info("Board: %s x %s" % (board.width, board.height))
    # logger.info("Food: %s" % board.food)

    our_snake = None
    enemy_snakes = []

    for snake_data in snakes:

        logger.info(snake_data)

        if snake_data['id'] == SNAKE_NAME:
            our_snake_data = snake_data
            logger.info("Got our snake: %s", our_snake_data)

        else:

            enemy_snakes.append(
                Snake(id=snake_data.get('id'),
                      state=snake_data.get('state'),
                      coords=snake_data.get('coords'),
                      turn=turn,
                      board=board,
                      last_eaten=snake_data.get('last_eaten'))
            )

    our_snake = Snake(id=our_snake_data.get('id'),
                      state=our_snake_data.get('state'),
                      coords=our_snake_data.get('coords'),
                      turn=turn,
                      board=board,
                      last_eaten=our_snake_data.get('last_eaten'),
                      enemies=enemy_snakes)

    direction = our_snake.move()

    taunt = ""

    if turn % 2 == 1:
        taunt = random.choice(TAUNTS)

    return {
        'move': direction,
        'taunt': taunt,
    }


@bottle.post('/end')
def end():
    data = bottle.request.json

    # TODO: Do things with data

    return {
        'taunt': random.choice(TAUNTS)
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    logger.info("Start snake")
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'), reloader=True)
