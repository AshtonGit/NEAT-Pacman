from enum import Enum
from datetime import datetime
import threading
from math import exp
from pathlib import Path
from time import sleep
import pygame
from neat.math_util import softmax
# ghosts and pacman positions are continous but the blocks that make the game up are discrete.
# Positions are floats. blocks are at integer positions. floats are between blocks. Each block is 1.0x1.0 dimensions
# this way movement can appear continouous but for ai purposes its discrete.


# board
# actors that hold positions
# tiles that hold static-gameobjects


class Tiles(Enum):
    EMPTY = 0
    WALL = 1
    CANDY = 2
    GATE = 3
    GHOST = 4
    PACMAN = 5


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
    [1, 1, 1, 1, 1, 1, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 2, 1, 0, 0, 0, 4, 4, 0, 0, 0, 0, 1, 2, 1, 1, 1, 1, 1, 1, 1],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1, 0, 4, 4, 0, 0, 1, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [1, 1, 1, 1, 1, 1, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 1, 1, 1, 1, 1, 1],
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

width = 27
height = 21


class GameObject:

    def __init__(self, color):
        self.color = color
        return

    def get_model(self):
        return


class Actor(GameObject):

    def __init__(self, color, position, speed, key, controller, fitness):
        super().__init__(color)
        self.position = position
        self.key = key
        self.controller = controller
        self.fitness = fitness
        self.field_of_view = (5, 5)
        self.size = 0.85 # actors are 17x17 pixels in size. Tiles are 20px. 17 is 0.85 of 20
        self.velocity = (0, 0)
        self.speed = speed

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
                print("Xpos",str(x_pos))
                print("Ypos",str(y_pos))
                print(str(x))
                print(str(y))
                raise e

    def update_velocity(self, velocity):
        self.velocity = velocity

    def next_move(self, tiles, pacman, ghosts):
        return 0

    def update_position(self, position):
        self.position = position

    def update_fitness(self, tiles):
        return

    # returns tuple where element 0 is controller id and element 1 is fitness
    def get_fitness_as_tuple(self):
        return self.key, self.fitness


class Pacman(Actor):

    def __init__(self, position, key, controller):
        super().__init__((0, 255, 255), position, 0.2, key, controller, 0)
        base_path = Path(__file__).parent
        asset_path = str((base_path / "../assets").resolve())
        self.models = {"left": pygame.image.load(asset_path + "/pacman-left.png"),
                       "right": pygame.image.load(asset_path + "/pacman-right.png"),
                       "up": pygame.image.load(asset_path + "/pacman-up.png"),
                       "down": pygame.image.load(asset_path + "/pacman-down.png"),
                       "closed": pygame.image.load(asset_path + "/pacman-closed.png")}
        self.facing = "left"
        self.open_close_time = datetime.now()
        self.is_closed = False
        self.size = 0.9 # pacman is 1x1 tile (20px), but need to make him slightly smaller to allow him to move thrghou
                        # one tile wide gaps

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
    # [ pacman.x, pacman.y, ghosts0.x, ghosts0.y..., ghostsN.x, ghostsN.y, self.view ]
    def next_move(self, tiles, pacman, ghosts):
        inputs = [self.position[1], self.position[0]]
        for ghost in ghosts:
            inputs.append(ghost.position[1])
            inputs.append(ghost.position[0])

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
            
            
class Ghost(Actor):

    def __init__(self, color, model, position, key, controller):
        super().__init__(color, position, 0.2, key, controller, 0)
        base_path = Path(__file__).parent
        asset_path = str((base_path / "../assets").resolve())
        self.models = {"left": pygame.image.load(asset_path + model + "-left.png"),
                       "right": pygame.image.load(asset_path + model + "-right.png")}
        self.facing = "left"
        self.size = 0.7 # ghosts are 0.7 tiles (14px) tall and wide

    def get_model(self):
        return self.models[self.facing]

    # increments for every second where ghosts position is within 4 tiles of pacman
    def update_fitness(self, seconds):
        self.fitness += seconds
        return

    # Actor's controllers analyses board state and returns what it thinks is the best direction to move in
    # pacman Controllers take inputs as a list of ints repesenting actor positions or tile contents, in following order
    # inputs = [pacman.x, pacman.y, self.x, self.y, ghosts0.x, ghosts0.y ..., ghostsN-1.x, ghostsN-1.y, self.view]
    def next_move(self, tiles, pacman, ghosts):
        inputs = [pacman.position[1], pacman.position[0], self.position[1], self.position[0]]
        for ghost in ghosts:
            if ghost is not self:
                inputs.append(ghost.position[1])
                inputs.append(ghost.position[0])
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
        # ghost only has left and right models so only change facing when x axis velocity changes
        if velocity[1] > 0:
            self.facing = "right"
        elif velocity[1] < 0:
            self.facing = "left"

        self.velocity = velocity


class Game:
    max_score = 226  # number of candys in the game

    # controllers = list of 5 controllers. Index 0 is always the pacman controller.
    def __init__(self, controllers):
        self.tiles = []
        self.game_over = False
        pacman_spawn = ()
        ghost_spawn = []

        for y in range(0, height):
            row = []
            for x in range(0, width):
                tile = init_tiles[y][x]
                row.append(tile)
                if tile == Tiles.PACMAN.value:
                    pacman_spawn = (y, x)
                elif tile == Tiles.GHOST.value:
                    ghost_spawn.append((y, x))
            self.tiles.append(row)

        self.pacman = Pacman(pacman_spawn, controllers["pacman"][0], controllers["pacman"][1])
        self.ghosts = []
        model_prefix = ["/ghost-red", "/ghost-blue", "/ghost-yellow", "/ghost-green"]
        for key, controller in controllers["ghosts"].items():
            self.ghosts.append(Ghost((255, 0, 0), model_prefix.pop(), ghost_spawn.pop(), key, controller))

    def play_game(self):
        #every second, update ghosts fitness
        g_fit_manager = threading.Thread(target=manage_ghost_fitness, args=(self,), daemon=True)
        g_fit_manager.start()
        # Game ends after 90 seconnds
        #end_game_if_timelimit_reached(self, 90)
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
            for ghost in self.ghosts:
                self.actors_next_move(ghost)

            self.update_actor_position(self.pacman)
            for ghost in self.ghosts:
                self.update_actor_position(ghost)
            # resolve pacman collision with candy and ghosts
            self.resolve_collisions()
            # end game if pacman eats all candy in level
            if self.pacman.fitness >= self.max_score:
                self.game_over = True
            sleep(0.06)

        # close threads
        g_fit_manager.join()
        end_game_stuck.join()
        end_game_time.join()
     #  display_thread.join()

        # return fitness of each network
        fitness = {}
        ghost_fitness = []
        fitness["pacman"] = self.pacman.get_fitness_as_tuple()
        for ghost in self.ghosts:
            ghost_fitness.append(ghost.get_fitness_as_tuple())
        fitness["ghost"] = ghost_fitness
        return fitness

    def actors_next_move(self, actor):
        move = actor.next_move(self.tiles, self.pacman, self.ghosts)
        velocity = self.build_velocity(actor, move)
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
    # If pacman collides with ghost, increase ghosts fitness and end game
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

        # if ghost collides with pacman, give it a large fitness score
        # coordinates are from top left so ghosts can miss out on hitting pacman
        # if they are moving down against a right or downwards wall as their position is always stuck at x.8
        for ghost in self.ghosts:
            x = int(ghost.position[1])
            y = int(ghost.position[0])
            if ghost.velocity[0] > 0:
                y += 1
                y = int(y)
            elif ghost.velocity[1] > 0:
                x += 1
                x = int(x)
            if int(pos[0]) == y and int(pos[1]) == x:
                ghost.update_fitness(50)
                self.game_over = True

    # if ghost is within 3 tiles of pacman, increase its fitness by 1
    def update_ghost_fitness(self):
        for ghost in self.ghosts:
            x_dist = abs(ghost.position[1] - self.pacman.position[1])
            y_dist = abs(ghost.position[0] - self.pacman.position[0])
            if y_dist <= 3.0 and x_dist <= 3.0:
                ghost.update_fitness(1)

    # return true if actor is able to move to next tile in given direction
    def direction_clear(self, actor, velocity):
        x = actor.position[1] + velocity[1]
        y = actor.position[0] + velocity[0]
        size = actor.size
        # to stop animation clipping when moving right or down as actor coordinates are their top left position
        # need to check both corners in direction moving
        if velocity[1] > 0: #moving right
            x = int(x + size)
            top_right = self.tiles[int(y)][x] # top right corner
            y = int(y + size)
            bottom_right = self.tiles[y][x] # bottom left corner
            return top_right != Tiles.WALL.value and bottom_right != Tiles.WALL.value
        elif velocity[0] > 0: # moving down
            y = int(y + size)
            bottom_left = self.tiles[y][int(x)]
            x = int(x + size)
            bottom_right = self.tiles[y][x]
            return bottom_left != Tiles.WALL.value and bottom_right != Tiles.WALL.value
        elif velocity[1] < 0: # moving left
            top_left = self.tiles[int(y)][int(x)]
            y = int(y + size)
            bottom_left = self.tiles[y][int(x)]
            return top_left != Tiles.WALL.value and bottom_left != Tiles.WALL.value
        elif velocity[0] < 0: #moving up
            top_left = self.tiles[int(y)][int(x)]
            x = int( x + size)
            top_right = self.tiles[int(y)][x]
            return top_left != Tiles.WALL.value and top_right != Tiles.WALL.value


    def build_velocity(self, actor, move):
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


def manage_ghost_fitness(game):
    # increase ghosts fitness by 1 for every second it spends within 3 tiles of pacman
    while not game.game_over:
        game.update_ghost_fitness()
        sleep(1)

def end_game_if_timelimit_reached(game, max_time):
    start = datetime.now()
    while not game.game_over:
        now = datetime.now()
        if (now - start).seconds >= max_time:
            game.game_over = True
        sleep(0.5)


# if no actors change position after timeout time, end the game to speed up training
def end_game_if_actors_stuck(game, timeout):
    duration_inactive = 0

    # get initial positions
    ghost_pos = {}
    for ghost in game.ghosts:
        ghost_pos[ghost.key] = ghost.position
    pacman_pos = game.pacman.position
    sleep(1)

    while not game.game_over:
        if duration_inactive == timeout:
            game.game_over = True
            return
        # check if positions have changed more than 0.5 tiles. This behavior where actors rapidly oscillate up and down
        # or stop moving entirely
        active = False
        for ghost in game.ghosts:
            ydelta = abs(ghost.position[0] - ghost_pos[ghost.key][0])
            xdelta = abs(ghost.position[1] - ghost_pos[ghost.key][1])
            if ydelta > 0.5 or xdelta > 0.5:
                ghost_pos[ghost.key] = ghost.position
                active = True
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
        sleep(0.8)


def softmax(values):
    """
    Compute the softmax of the given value set, v_i = exp(v_i) / s,
    where s = sum(exp(v_0), exp(v_1), ..)."""
    e_values = []
    """Take away the maximum value from each entry before softmaxing. Algebraicly this is the same but ensures the
     largest value ever passed into exp is 1, preventing overflow errors"""
    mx = max(values)
    for v in values:
        v = v - mx
        ev = exp(v)
        e_values.append(ev)
    s = sum(e_values)
    inv_s = 1.0 / s
    return [ev * inv_s for ev in e_values]