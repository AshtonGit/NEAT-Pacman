import unittest

from Lib.pacman.pacman_with_ghosts.game import Game


class MyTestCase(unittest.TestCase):

    def test_ghost_fitness_updates_with_distance(self):
        game = Game({1: None, 2: None, 3: None, 4: None, 5: None})
        ghost = game.ghosts[0]
        ghost.update_position((0, 0))
        game.pacman.update_position((1, 0))
        game.update_ghost_fitness()
        self.assertEqual(ghost.fitness, 1)
        ghost.update_position((4, 4))
        game.update_ghost_fitness()
        self.assertEqual(ghost.fitness, 1)

    def test_velocity_matches_move(self):
        # 0 = left, 1 = right, 2 = uupd, 3 =down
        game = Game({1: None, 2: None, 3: None, 4: None, 5: None})
        ghost = game.ghosts[0]
        speed = ghost.speed
        v = game.build_velocity(ghost, 0)
        self.assertEqual(v, (0, -speed))
        v = game.build_velocity(ghost, 1)
        self.assertEqual(v, (0, speed))
        v = game.build_velocity(ghost, 2)
        self.assertEqual(v, (-speed, 0))
        v = game.build_velocity(ghost, 3)
        self.assertEqual(v, (speed, 0))

    def test_wall_collision(self):
        game = Game({1: None, 2: None, 3: None, 4: None, 5: None})
        pacman = game.pacman
        pacman.update_position((1, 1))
        pacman.velocity = (-1, 0)
        game.update_actor_position(pacman)
        self.assertEqual(pacman.position, (1.5, 1))

    def test_candy_consumption(self):
        game = Game({1: None, 2: None, 3: None, 4: None, 5: None})
        pacman = game.pacman
        pacman.update_position((1, 1))
        pacman.velocity = (0, 1)
        game.resolve_collisions()
        self.assertEqual(pacman.fitness, 1)

    def test_pacman_ghost_collision(self):
        game = Game({1: None, 2: None, 3: None, 4: None, 5: None})
        pacman = game.pacman
        ghost = game.ghosts[0]
        pacman.update_position((1, 1))
        pacman.velocity = (0, 1)
        ghost.update_position((1, 1))
        game.resolve_collisions()
        self.assertEqual(ghost.fitness, 10)
        self.assertEqual(game.game_over, True)

    def test_change_direction_if_way_clear(self):
        game = Game({1: None, 2: None, 3: None, 4: None, 5: None})
        pacman = game.pacman
        pacman.update_position((1, 1))
        pacman.velocity = (-1, 0)
        velocity = (0, 1)
        game.update_actor_velocity_if_clear(pacman, velocity)
        self.assertEqual(pacman.velocity, (0, 1))

    def test_maintain_direction_if_way_blocked(self):
        game = Game({1: None, 2: None, 3: None, 4: None, 5: None})
        pacman = game.pacman
        pacman.update_position((1, 1))
        pacman.velocity = (0, 1)
        velocity = (-1, 0)
        game.update_actor_velocity_if_clear(pacman, velocity)
        self.assertEqual(pacman.velocity, (0, 1))


class TestGameTimer(unittest.TestCase):

    def test_game_ends_max_time(self):
        return

    def test_game_ends_no_action_timeout(self):
        return


class MockController:

    def __init__(self):
        return

    def activate(self, input):
        return [0, 1, 1, 2, 0]

if __name__ == '__main__':
    unittest.main()
