"""Uses `pickle` to save and restore populations (and other aspects of the simulation state)."""
from __future__ import print_function

import gzip
import random
from Lib.pacman.pacman_exclusive.pacman_population import PacmanPopulation

try:
    import cPickle as pickle  # pylint: disable=import-error
except ImportError:
    import pickle  # pylint: disable=import-error


class PacmanCheckpointer:

    def __init__(self, generation_interval, filename_prefix='neat-checkpoint-'):
        self.generation_interval = generation_interval
        self.current_generation = 0
        self.last_generation_checkpoint = self.current_generation - generation_interval
        self.filename_prefix = filename_prefix

    def start_generation(self, generation):
        self.current_generation = generation

    def end_generation(self, config, population, species):
        checkpoint_due = False

        if (checkpoint_due is False) and (self.generation_interval is not None):
            dg = self.current_generation - self.last_generation_checkpoint
            if dg >= self.generation_interval:
                checkpoint_due = True

        if checkpoint_due:
            self.save_checkpoint(config, population, species, self.current_generation)
            self.last_generation_checkpoint = self.current_generation

    def save_checkpoint(self, config,  population, species, generation):
        """ Save the current simulation state. """
        filename = '{0}{1}'.format(self.filename_prefix, generation)
        print("Saving checkpoint to {0}".format(filename))

        with gzip.open(filename, 'w', compresslevel=5) as f:
            data = (generation, config,  population, species, random.getstate())
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def restore_checkpoint(filename):
        """Resumes the simulation from a previous saved point."""
        with gzip.open(filename) as f:
            generation, config,  population, species, rndstate = pickle.load(f)
            random.setstate(rndstate)
            return PacmanPopulation(config,
                                       initial_state=( population, species, generation))
