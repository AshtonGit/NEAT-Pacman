
from Lib.pacman.pacman_exclusive.simulation import PacmanExclusiveSimulation
from Lib.pacman.pacman_with_ghosts.simulation import PacmanGhostSimulation
from pathlib import Path


base_path = Path(__file__).parent
pacman_ghost_config_path = (base_path / "../conf/config.conf").resolve()
pacman_exclusive_config_path = (base_path / "../conf/pacman_only_config.conf").resolve()
checkpoint_path = (base_path / "neat-checkpoint-924").resolve()


""" Uncomment these 3 lines to run a new simulation without using the text interface"""
"""
sim = PacmanExclusiveSimulation()
pop = sim.new_population(pacman_exclusive_config_path)
sim.run_simulation(pop, generations=20)
"""


print("Welcome to NEAT-Pacman")
print("An evolutionary simulation which generates neural network algorithms that play Pacman")

while True:
    print("type 'help' for a list of commands")
    cmd = input("")
    split = cmd.split(' ')
    try:
        if cmd == 'help':
            print("type 'help name' to find out more about the command 'name'")
            print("pacman-exclusive [action] [file] [generations]")
            print("pacman-ghost [action] [file] [generations]")
            print("\t[action]       -'load' an existing population from checkpoint file"
                  "\n\t               -'new' create new population from config file")
            print("\t[file]         -File path to config file if new simulation or checkpoint file if loading."
                  "\n\t                All file paths are relative to the directory this program is located in")
            print("\t[generations]  -How many generations the simulation will run for")

            print("eg pacman-exclusive new ../config/pacman_only_config.conf 50")

        else:
            game_mode = split[0]
            action = split[1]
            file = split[2]
            generation = split[3]
            if game_mode == 'pacman-exclusive':
                sim = PacmanExclusiveSimulation()
                if action == 'new':
                    pop = sim.new_population(file)
                    sim.run_simulation(pop, int(generation))
                elif action == 'load':
                    pop = sim.restore_checkpoint(file)
                    sim.run_simulation(pop, int(generation))

            elif game_mode == 'pacman-ghost':
                sim = PacmanGhostSimulation()
                if action == 'new':
                    pop = sim.new_population(file)
                    sim.run_simulation(pop, int(generation))
                elif action == 'load':
                    pop = sim.restore_checkpoint(file)
                    sim.run_simulation(pop, int(generation))
    except IndexError or TypeError:
        continue

