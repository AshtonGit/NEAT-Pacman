
from Lib.pacman.pacman_exclusive.simulation import PacmanExclusiveSimulation

from pathlib import Path


base_path = Path(__file__).parent
pacman_ghost_config_path = (base_path / "../conf/config.conf").resolve()
pacman_exclusive_config_path = (base_path / "../conf/pacman_only_config.conf").resolve()
checkpoint_path = (base_path / "neat-checkpoint-924").resolve()

sim = PacmanExclusiveSimulation()
pop = sim.new_population(pacman_exclusive_config_path)
#pop = sim.restore_checkpoint(checkpoint_path)
sim.run_simulation(pop, 500)