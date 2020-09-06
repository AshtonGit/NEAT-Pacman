import sys
import threading
from datetime import datetime
import neat
import pygame
from Lib.pacman.pacman_exclusive.view import View
from Lib.pacman.pacman_exclusive.evolution import eval_genomes
from Lib.pacman.pacman_exclusive.pacman_population import PacmanPopulation
from Lib.pacman.pacman_exclusive.pacman_checkpointer import PacmanCheckpointer

class PacmanExclusiveSimulation:

    def __init__(self):
        pygame.init()
        self.view = View()

    def run_simulation(self, population, generations):
        simulation_started = False
        last_update = datetime.now()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

            if not simulation_started:
                simulation = threading.Thread(target=population.run, args=(eval_genomes, generations), daemon=True)
                simulation.start()
                simulation_started = True

            # update view every 16.7 milliseconds, AKA 60 frames per second
            now = datetime.now()
            delta = (now - last_update).microseconds
            delta = delta * 1000
            if delta >= 16.7:
                self.view.update()
                last_update = now

    def new_population(self, config_file):
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                             neat.DefaultStagnation, config_file)
        # create a population
        p = PacmanPopulation(config, checkpointers=[PacmanCheckpointer(4)], view=self.view)

        # add a stdout reporter to show progress in terminal
        p.add_reporter(neat.StdOutReporter(True))

        stats = neat.StatisticsReporter()
        p.add_reporter(stats)
        p.add_checkpointer(PacmanCheckpointer(4))
        return p

    def restore_checkpoint(self, filename):
        pop = PacmanCheckpointer.restore_checkpoint(filename)
        pop.view = self.view
        pop.add_checkpointer(PacmanCheckpointer(25))
        pop.add_reporter(neat.StdOutReporter(True))
        pop.add_reporter(neat.StatisticsReporter())
        return pop
