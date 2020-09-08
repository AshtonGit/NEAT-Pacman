from Lib.pacman.pacman_with_ghosts.game import Tiles, softmax, width, height
from datetime import datetime
import threading
from pathlib import Path
from time import sleep
import pygame

# 27 wide x 21 tall = 621
init_tiles = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1],
    [1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1],
    [1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 2, 1, 0, 0, 0, 2, 2, 2, 0, 0, 0, 1, 2, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 2, 1, 0, 0, 0, 2, 1, 2, 0, 0, 0, 1, 2, 1, 1, 1, 1, 1, 1, 1],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1, 0, 2, 1, 2, 0, 1, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [1, 1, 1, 1, 1, 1, 1, 2, 1, 0, 0, 0, 2, 2, 2, 0, 0, 0, 1, 2, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 5, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 1],
    [1, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 1, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]


def end_game_if_timelimit_reached(game, max_time):
    start = datetime.now()
    while not game.game_over:
        now = datetime.now()
        if (now - start).seconds >= max_time:
            game.game_over = True
        sleep(0.5)


# if no actors change position before timeout, end the game to speed up training
def end_game_if_actors_stuck(game, timeout):
    duration_inactive = 0
    pacman_pos = game.pacman.position
    sleep(1)

    while not game.game_over:
        if duration_inactive == timeout:
            game.game_over = True
            return
        # check if positions have changed more than 0.5 tiles. This behavior where actors rapidly oscillate up and down
        # or stop moving entirely
        active = False
        xdelta = abs(pacman_pos[1] - game.pacman.position[1])
        ydelta = abs(pacman_pos[0] - game.pacman.position[0])
        if ydelta > 0.5 or xdelta > 0.5:
            pacman_pos = game.pacman.position
            active = True
        if not active:
            duration_inactive += 1
        else:
            duration_inactive = 0
        # check position every second
        sleep(0.5)


def build_velocity(actor, move):
    if move == 0:
        # (y, x)
        return 0, -actor.speed
    elif move == 1:
        return 0, actor.speed
    elif move == 2:
        return -actor.speed, 0
    elif move == 3:
        return actor.speed, 0
    return actor.velocity


class Pacman:

    def __init__(self, position, key, controller, speed=0.4, color=(0, 255, 255)):
        self.color = color
        self.position = position
        self.key = key
        self.controller = controller
        self.field_of_view = (5, 5)
        self.size = 0.85  # actors are 17x17 pixels in size. Tiles are 20px. 17 is 0.85 of 20
        self.velocity = (0, 0)
        self.speed = speed
        self.fitness = 0

        base_path = Path(__file__).parent.parent
        asset_path = str((base_path / "../assets").resolve())
        self.models = {"left": pygame.image.load(asset_path + "/pacman-left.png"),
                       "right": pygame.image.load(asset_path + "/pacman-right.png"),
                       "up": pygame.image.load(asset_path + "/pacman-up.png"),
                       "down": pygame.image.load(asset_path + "/pacman-down.png"),
                       "closed": pygame.image.load(asset_path + "/pacman-closed.png")}
        self.facing = "left"
        self.open_close_time = datetime.now()
        self.is_closed = False
        self.size = 0.9  # pacman is 1x1 tile (20px), but need to make him slightly smaller to allow him to move thrghou
        # one tile wide gaps

    def get_vision(self, tiles):

        x_w = int(self.field_of_view[1] / 2)
        y_w = int(self.field_of_view[0] / 2)

        x_pos = self.position[1]
        y_pos = self.position[0]

        # view is centered at character position
        x = x_pos
        y = y_pos

        # if view would go out of bounds in either direction, adjust view to fit
        if x_pos + x_w >= width:
            x = width - self.field_of_view[1] - 1
        elif x_pos - x_w < 0:
            x = 0
        else:
            x = x - x_w

        if y_pos + y_w >= height:
            y = height - self.field_of_view[0] - 1
        elif y_pos - y_w < 0:
            y = 0
        else:
            y = y - y_w

        try:
            # get tile data for tiles in that fall in actors field of view
            vision = []
            y = int(y)
            x = int(x)
            for i in range(y, y + self.field_of_view[1]):
                row = []
                for j in range(x, x + self.field_of_view[0]):
                    row.append(tiles[i][j])
                vision.append(row)
            return vision
        except IndexError as e:
            print(e)
            print("Xpos", str(x_pos))
            print("Ypos", str(y_pos))
            print(str(x))
            print(str(y))
            raise e

    def update_position(self, position):
        self.position = position

    # returns tuple where element 0 is controller id and element 1 is fitness
    def get_fitness_as_tuple(self):
        return self.key, self.fitness

    # Return a sprite image representing pacmans current state or direction
    # pacman opens and closes his mouth every 0.4 seconds
    def get_model(self):
        delta = datetime.now() - self.open_close_time
        if delta.microseconds / 10000 > 20:
            self.is_closed = not self.is_closed
            self.open_close_time = datetime.now()
        if self.is_closed:
            return self.models["closed"]
        else:
            return self.models[self.facing]

    # increments for every candy eaten
    def update_fitness(self, candy_eaten):
        self.fitness += candy_eaten
        return

    # Actor's controllers analyses board state and returns what it thinks is the best direction to move in
    # pacman Controllers take inputs  as a list of ints in following order
    # [ pacman.x, pacman.y, self.view ]
    def next_move(self, tiles, pacman):
        inputs = [self.position[1], self.position[0]]
        vision = self.get_vision(tiles)
        for row in vision:
            inputs += row
        output = self.controller.activate(inputs)
        # transform output into multi-classifier output via softmax activation function
        # softmax transforms all outputs so that their values range from (0, 1) and sum to 1.0
        softmaxed = softmax(output)
        # the output node with the max value is the chosen class / move
        return softmaxed.index(max(softmaxed))

    def update_velocity(self, velocity):
        if velocity[0] > 0:
            self.facing = "down"
        elif velocity[0] < 0:
            self.facing = "up"
        elif velocity[1] > 0:
            self.facing = "right"
        else:
            self.facing = "left"
        self.velocity = velocity



class Game:
    max_score = 226  # number of candys in the game

    # controllers = list of 5 controllers. Index 0 is always the pacman controller.
    def __init__(self, controller):
        self.tiles = []
        self.game_over = False
        pacman_spawn = ()
        for y in range(0, height):
            row = []
            for x in range(0, width):
                tile = init_tiles[y][x]
                row.append(tile)
                if tile == Tiles.PACMAN.value:
                    pacman_spawn = (y, x)
            self.tiles.append(row)
        self.pacman = Pacman(pacman_spawn, "Pacman", controller)

    def play_game(self):
        # Game ends after 90 seconds
        # end_game_if_timelimit_reached(self, 90)
        end_game_time = threading.Thread(target=end_game_if_timelimit_reached, args=(self, 90), daemon=True)
        end_game_time.start()
        # Game ends if no actor changes position after 1 seconds
        end_game_stuck = threading.Thread(target=end_game_if_actors_stuck, args=(self, 1), daemon=True)
        end_game_stuck.start()
        # start display to show game state to human viewer

        #   display_thread = threading.Thread(target=view.display_game, args=(self,), daemon=True)
        #    display_thread.start()
        while not self.game_over:
            self.actors_next_move(self.pacman)
            self.update_actor_position(self.pacman)
            # resolve pacman collision with candy
            self.resolve_collisions()
            # end game if pacman eats all candy in level
            if self.pacman.fitness >= self.max_score:
                self.game_over = True
            sleep(0.06)

        # close threads
        end_game_stuck.join()
        end_game_time.join()
        #  display_thread.join()

        # return fitness of each network
        fitness = self.pacman.fitness
        return fitness

    def actors_next_move(self, actor):
        move = actor.next_move(self.tiles, self.pacman)
        velocity = build_velocity(actor, move)
        self.update_actor_velocity_if_clear(actor, velocity)

    def update_actor_velocity_if_clear(self, actor, velocity):
        if velocity != actor.velocity:
            if self.direction_clear(actor, velocity):
                actor.update_velocity(velocity)

    # if new position is on a wall tile, do nothing
    # otherwise update position according to velocity
    def update_actor_position(self, actor):
        if self.direction_clear(actor, actor.velocity):
            nx = actor.position[1] + actor.velocity[1]
            ny = actor.position[0] + actor.velocity[0]
            actor.update_position((ny, nx))

    # If pacman collides with a candy, increase fitness
    def resolve_collisions(self):
        pos = self.pacman.position
        y = int(pos[0])
        x = int(pos[1])
        # when moving right or down, coordinates are taken from top left so pacman can miss out on candies
        if self.pacman.velocity[0] > 0:
            y += 1
            y = int(y)
        elif self.pacman.velocity[1] > 0:
            x += 1
            x = int(x)

        tile = self.tiles[y][x]
        if tile == Tiles.CANDY.value:
            self.pacman.update_fitness(1)
            self.tiles[y][x] = Tiles.EMPTY.value

    # return true if actor is able to move to next tile in given direction
    def direction_clear(self, actor, velocity):
        x = actor.position[1] + velocity[1]
        y = actor.position[0] + velocity[0]
        size = actor.size
        # to stop animation clipping when moving right or down as actor coordinates are their top left position
        # need to check both corners in direction moving
        if velocity[1] > 0:  # moving right
            x = int(x + size)
            top_right = self.tiles[int(y)][x]  # top right corner
            y = int(y + size)
            bottom_right = self.tiles[y][x]  # bottom left corner
            return top_right != Tiles.WALL.value and bottom_right != Tiles.WALL.value
        elif velocity[0] > 0:  # moving down
            y = int(y + size)
            bottom_left = self.tiles[y][int(x)]
            x = int(x + size)
            bottom_right = self.tiles[y][x]
            return bottom_left != Tiles.WALL.value and bottom_right != Tiles.WALL.value
        elif velocity[1] < 0:  # moving left
            top_left = self.tiles[int(y)][int(x)]
            y = int(y + size)
            bottom_left = self.tiles[y][int(x)]
            return top_left != Tiles.WALL.value and bottom_left != Tiles.WALL.value
        elif velocity[0] < 0:  # moving up
            top_left = self.tiles[int(y)][int(x)]
            x = int(x + size)
            top_right = self.tiles[int(y)][x]
            return top_left != Tiles.WALL.value and top_right != Tiles.WALL.value

