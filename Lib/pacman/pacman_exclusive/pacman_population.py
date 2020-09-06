import neat
from neat.math_util import mean
from neat.reporting import ReporterSet

from Lib.pacman.pacman_with_ghosts.view import View


class PacmanPopulation(neat.Population):

    def __init__(self, config, initial_state=None, checkpointers=None, view=None):
        super().__init__(config, None)
        self.reporters = ReporterSet()
        self.checkpointers = checkpointers

        if view is None:
            self.view = View()
        else:
            self.view = view

        self.config = config
        stagnation = config.stagnation_type(config.stagnation_config, self.reporters)
        self.reproduction = config.reproduction_type(config.reproduction_config,
                                                     self.reporters,
                                                     stagnation)
        if config.fitness_criterion == 'max':
            self.fitness_criterion = max
        elif config.fitness_criterion == 'min':
            self.fitness_criterion = min
        elif config.fitness_criterion == 'mean':
            self.fitness_criterion = mean
        elif not config.no_fitness_termination:
            raise RuntimeError(
                "Unexpected fitness_criterion: {0!r}".format(config.fitness_criterion))

        if initial_state is None:
            # Create a population from scratch, then partition into species.
            self.population = self.reproduction.create_new(config.genome_type,
                                                           config.genome_config,
                                                           config.pop_size)
            self.species = config.species_set_type(config.species_set_config, self.reporters)

            self.generation = 0
            self.species.speciate(config, self.population, self.generation)

        else:
            self.population, self.species, self.generation = initial_state

        self.best_genome = None

    def run(self, fitness_function, n=None):

        """
        Runs NEAT's genetic algorithm for at most n generations.  If n
        is None, run until solution is found or extinction occurs.
        The user-provided fitness_function must take only three arguments:
            1. Two populations as lists of (genome id, genome) tuples.
            2. The current configuration object.
        The return value of the fitness function is ignored, but it must assign
        a Python float to the `fitness` member of each genome.
        The fitness function is free to maintain external state, perform
        evaluations in parallel, etc.
        It is assumed that fitness_function does not modify the list of genomes,
        the genomes themselves (apart from updating the fitness member),
        or the configuration object.
        """
        if self.config.no_fitness_termination and (n is None):
            raise RuntimeError("Cannot have no generational limit with no fitness termination")

        k = 0
        while n is None or k < n:
            k += 1

            self.reporters.start_generation(self.generation)
            for checkpointer in self.checkpointers:
                checkpointer.start_generation(self.generation)

            # Evaluate all genomes using the user-provided function.
            fitness_function(list(self.population.items()), self.config, self.view)

            # Gather and report statistics.

            best_genome = None
            for p in self.population.values():
                if p.fitness is None:
                    raise RuntimeError("Fitness not assigned to genome {}".format(p.key))

                if best_genome is None or p.fitness > best_genome.fitness:
                    best_genome = p
            self.reporters.info("Ghost Generation: " + str(self.generation))
            self.reporters.post_evaluate(self.config, self.population, self.species, best_genome)

            # Track the best ghost genome ever seen.
            if self.best_genome is None or best_genome.fitness > self.best_genome.fitness:
                self.best_genome = best_genome

            if not self.config.no_fitness_termination:
                # End if the fitness threshold is reached.
                fv = self.fitness_criterion(g.fitness for g in self.population.values())
                if fv >= self.config.fitness_threshold:
                    self.reporters.info("\nBest Genome Found:\n")
                    self.reporters.found_solution(self.config, self.generation, best_genome)
                    break

            # Create the next ghost generation from the current generation.
            self.population = self.reproduction.reproduce(self.config, self.species,
                                                          self.config.pop_size, self.generation)
            if not self.species.species:
                self.reporters.info("\nComplete Extinction!")
                self.reporters.complete_extinction()
                if self.config.reset_on_extinction:
                    self.population = self.reproduction.create_new(self.config.genome_type,
                                                                   self.config.genome_config,
                                                                   self.config.pop_size)
                else:
                    raise CompleteExtinctionException()

            # Divide the new population into species.
            self.species.speciate(self.config, self.population, self.generation)
            self.reporters.end_generation(self.config, self.population, self.species)

            for checkpoint in self.checkpointers:
                checkpoint.end_generation(self.config, self.population, self.species)
            self.generation += 1

        if self.config.no_fitness_termination:
            self.reporters.info("\nSolution Found!")
            self.reporters.found_solution(self.config, self.generation, self.best_genome)

        return self.best_genome

    def add_checkpointer(self, checkpointer):
        if self.checkpointers is None:
            self.checkpointers = [checkpointer]
        else:
            self.checkpointers.append(checkpointer)


class CompleteExtinctionException(Exception):
    pass
