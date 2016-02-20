
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

class Filter(object):

    actions = None
    priority = 0

    def __init__(self, priority=0):
        from models import Snake
        self.actions = []
        self.priority = priority

    def apply(self, snake, actions):

        raise NotImplementedError('implement this in the child object!')

    def remove_action(self, action):
        from models import Snake

        if len(self.actions) > 1:
            try:
                self.actions.remove(action)
            except Exception:
                pass


class WallFilter(Filter):

    def apply(self, snake, actions):
        from models import Snake

        self.actions = actions
        if snake.head_x == 0:
            #logger.info("Wallfilter head_x == 0: removing LEFT")
            self.remove_action(Snake.LEFT)

        if snake.head_x == snake.board.width - 1:
            #logger.info("Wallfilter head_x == %s: removing RIGHT", snake.board.width-1)
            self.remove_action(Snake.RIGHT)

        if snake.head_y == 0:
            #logger.info("Wallfilter head_y == 0: removing UP")
            self.remove_action(Snake.UP)

        if snake.head_y == snake.board.height - 1:
            #logger.info("Wallfilter head_y == %s: removing DOWN", snake.board.height-1)
            self.remove_action(Snake.DOWN)

        logger.info("Applied wall filter: %s", self.actions)

        return self.actions


class SelfFilter(Filter):

    def apply(self, snake, actions):
        from models import Snake

        self.actions = actions
        for x, y in snake.coords:

            if snake.head_y == y:
                if snake.head_x + 1 == x:
                    self.remove_action(Snake.RIGHT)

                if snake.head_x - 1 == x:
                    self.remove_action(Snake.LEFT)

            if snake.head_x == x:

                if snake.head_y + 1 == y:
                    self.remove_action(Snake.DOWN)

                if snake.head_y - 1 == y:
                    self.remove_action(Snake.UP)
        logger.info("actions %s" % self.actions)
        return self.actions


class EnemyFilter(Filter):

    def apply(self, snake, actions):
        from models import Snake

        self.actions = actions

        snakes = snake.enemies

        for this_snake in snakes:

            # skip if this is me...
            if this_snake.id == snake.id:
                continue

            for x, y in this_snake.coords:
                if snake.head_y == y:
                    if snake.head_x + 1 == x:
                        self.remove_action(Snake.RIGHT)

                    if snake.head_x - 1 == x:
                        self.remove_action(Snake.LEFT)

                if snake.head_x == x:

                    if snake.head_y + 1 == y:
                        self.remove_action(Snake.DOWN)

                    if snake.head_y - 1 == y:
                        self.remove_action(Snake.UP)

        logger.info("actions %s" % self.actions)

        return self.actions


class FoodFilter(Filter):
    closest_food = None
    closest_food_distance = None

    def apply(self, snake, actions):
        self.actions = actions
        from models import Snake

        logger.info("Applying food filter, actions %s" % self.actions)

        for food in snake.board.food:
            food_distance = food.distance(snake.head_x, snake.head_y)

            if not self.closest_food:

                self.closest_food = food
                self.closest_food_distance = food_distance

            else:

                if food_distance < self.closest_food_distance:

                    if snake.enemies:
                        for enemy in snake.enemies:
                            # If no other snake is closer to this food, get it!
                            if food.distance(enemy.head_x, enemy.head_y) < self.closest_food_distance:
                                self.closest_food = food
                                self.closest_food_distance = food_distance
                    else:
                        self.closest_food = food
                        self.closest_food_distance = food_distance

        if self.closest_food.x > snake.head_x:

            self.remove_action(Snake.LEFT)

        elif self.closest_food.x < snake.head_x:

            self.remove_action(Snake.RIGHT)

        else:

            self.remove_action(Snake.LEFT)
            self.remove_action(Snake.RIGHT)

        if self.closest_food.y > snake.head_y:

            self.remove_action(Snake.UP)

        elif self.closest_food.y < snake.head_y:

            self.remove_action(Snake.DOWN)

        else:

            self.remove_action(Snake.UP)
            self.remove_action(Snake.DOWN)

        logger.info("actions %s" % self.actions)

        return self.actions


class DontWreckYoSelfFilter(Filter):

    def apply(self, snake, actions):
        self.actions = actions

        from models import Snake

        if snake.health <= 97:
            return self.actions

        if len(self.actions) <= 1:
            return self.actions

        if Snake.UP in self.actions:

            next_x, next_y = snake.head_x, snake.head_y - 1

            for x, y in snake.coords:

                if next_y == y:
                    if next_x + 1 == x:
                        self.remove_action(Snake.UP)

                if next_x - 1 == x:
                    self.remove_action(Snake.UP)

                if next_x == x:
                    if next_y - 1 == y:
                        self.remove_action(Snake.UP)

        if Snake.DOWN in self.actions:

            next_x, next_y = snake.head_x, snake.head_y + 1

            for x, y in snake.coords:

                if next_y == y:
                    if next_x + 1 == x:
                        self.remove_action(Snake.DOWN)

                    if next_x - 1 == x:
                        self.remove_action(Snake.DOWN)

                if next_x == x:
                    if next_y + 1 == y:
                        self.remove_action(Snake.DOWN)

        if Snake.LEFT in self.actions:

            next_x, next_y = snake.head_x - 1, snake.head_y

            for x, y in snake.coords:

                if next_y == y:
                    if next_x - 1 == x:
                        self.remove_action(Snake.LEFT)

                if next_x == x:
                    if next_y + 1 == y:
                        self.remove_action(Snake.LEFT)

                    if next_y - 1 == y:
                        self.remove_action(Snake.LEFT)

        if Snake.RIGHT in self.actions:

            next_x, next_y = snake.head_x + 1, snake.head_y

            for x, y in snake.coords:

                if next_y == y:
                    if next_x - 1 == x:
                        self.remove_action(Snake.RIGHT)

                if next_x == x:
                    if next_y + 1 == y:
                        self.remove_action(Snake.RIGHT)

                    if next_y - 1 == y:
                        self.remove_action(Snake.RIGHT)

        logger.info("actions %s" % self.actions)

        return self.actions



class HeadOnLookAheadFilter(Filter):

    def apply(self, snake, actions):
        from models import Snake

        self.actions = actions
        snakes = snake.enemies

        for this_snake in snakes:

            # skip if this is me...
            if this_snake.id == snake.id:
                continue

            potential_benefit_positions = []

            for action in self.actions:

                if action == Snake.UP:
                    logger.info("Considering UP")
                    logger.info("actions %s" % self.actions)
                    attackables = self.get_attackables_in_proximity(snake.head_x, snake.head_y-1, snake.enemies, len(snake.coords))

                    if attackables:
                        potential_benefit_positions.append(Snake.UP)

                    for attackable in self.run_away_from(snake.head_x, snake.head_y-1, snake.enemies, len(snake.coords)):
                        if attackable.length >= snake.length:
                            self.remove_action(Snake.UP)

                elif action == Snake.DOWN:
                    logger.info("Considering DOWN")
                    logger.info("actions %s" % self.actions)
                    attackables = self.get_attackables_in_proximity(snake.head_x, snake.head_y+1, snake.enemies, len(snake.coords))

                    for attackable in self.run_away_from(snake.head_x, snake.head_y+1, snake.enemies, len(snake.coords)):
                        if attackable.length >= snake.length:
                            self.remove_action(Snake.DOWN)

                    if attackables:
                        potential_benefit_positions.append(Snake.DOWN)

                elif action == Snake.LEFT:
                    logger.info("Considering LEFT")
                    logger.info("actions %s" % self.actions)
                    attackables = self.get_attackables_in_proximity(snake.head_x-1, snake.head_y, snake.enemies, len(snake.coords))

                    for attackable in self.run_away_from(snake.head_x-1, snake.head_y, snake.enemies, len(snake.coords)):
                        if attackable.length >= snake.length:
                            self.remove_action(Snake.LEFT)

                    if attackables:
                        potential_benefit_positions.append(Snake.LEFT)

                elif action == Snake.RIGHT:
                    logger.info("Considering RIGHT")
                    logger.info("actions %s" % self.actions)
                    attackables = self.get_attackables_in_proximity(snake.head_x+1, snake.head_y, snake.enemies, len(snake.coords))

                    for attackable in self.run_away_from(snake.head_x+1, snake.head_y, snake.enemies, len(snake.coords)):
                        if attackable.length >= snake.length:
                            self.remove_action(Snake.RIGHT)

                    if attackables:
                        potential_benefit_positions.append(Snake.RIGHT)

            # If there is an optimal position, remove any actions that are not it
            for action in self.actions:
                if len(potential_benefit_positions) > 0 and action not in potential_benefit_positions:
                    self.remove_action(action)

        logger.info("actions %s" % self.actions)
        return self.actions

    def get_attackables_in_proximity(self, x, y, enemies, my_length):

        attackables = []

        for enemy in enemies:
            enemy_len = len(enemy.coords)

            if my_length < enemy_len:
                continue

            if enemy.head_y == y-1:
                if x-1 <= enemy.head_x <= x+1:
                    attackables.append(enemy)

            if enemy.head_y == y:
                if x-1 <= enemy.head_x <= x+1:
                    attackables.append(enemy)

            if enemy.head_y == y+1:
                if x-1 <= enemy.head_x <= x+1:
                    attackables.append(enemy)

        return attackables

    def run_away_from(self, x, y, enemies, my_length):

        run_from = []

        for enemy in enemies:
            enemy_len = len(enemy.coords)

            if my_length < enemy_len:
                continue

            if enemy.head_y == y-1:
                if x-1 <= enemy.head_x <= x+1:
                    run_from.append(enemy)

            if enemy.head_y == y:
                if x-1 <= enemy.head_x <= x+1:
                    run_from.append(enemy)

            if enemy.head_y == y+1:
                if x-1 <= enemy.head_x <= x+1:
                    run_from.append(enemy)

        return run_from

