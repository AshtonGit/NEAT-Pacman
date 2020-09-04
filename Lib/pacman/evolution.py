import neat
import random
from Lib.pacman.game import Game


# Only run as a demon thread. This ends the program window if pygame closed
# Function handling events prevents simulation view from freezing when minimized
# Run as a demon so that if program closed by other sources the thread is ended.

def eval_genomes(pacman_genomes, ghost_genomes, configuration, view):
    ghosts = {}
    pacmen = {}
    for i in range(len(ghost_genomes)):
        ghosts[i] = {"network": neat.nn.FeedForwardNetwork.create(ghost_genomes[i][1], configuration), "fitness": 0,
                     "games": 0}

    for i in range(len(pacman_genomes)):
        pacmen[i] = {"network": neat.nn.FeedForwardNetwork.create(pacman_genomes[i][1], configuration), "fitness": 0,
                     "games": 0}

    groups = create_groups(pacmen, ghosts)
    for bracket in groups:
        # play game to asses fitness of eachn genome
        fitness = play_pacman_game(bracket, view)
        # increment game counter and fitness
        pacman_id = bracket["pacman"][0]
        pacmen[pacman_id]["games"] += 1
        pacmen[pacman_id]["fitness"] += fitness["pacman"][1]

        for k, f in fitness["ghost"]:
            if fitness is None:
                nof = True
            ghosts[k]["games"] += 1
            ghosts[k]["fitness"] += f

    # Final fitness for every genome is their average score across all games played
    for i in range(len(ghost_genomes)):
        ghost_fitness = ghosts[i]['fitness'] / ghosts[i]['games']
        ghost_genomes[i][1].fitness = ghost_fitness

    for i in range(len(pacman_genomes)):
        pacman_fitness = pacmen[i]["fitness"] / pacmen[i]["games"]
        pacman_genomes[i][1].fitness = pacman_fitness


def play_pacman_game(controllers, view):
    game = Game(controllers)
    view.set_game(game)
    fitness = game.play_game()
    return fitness


def create_groups(pacman_networks, ghost_networks):
    pac_pop = len(pacman_networks)
    ghost_pop = len(ghost_networks)
    shuffled = random.sample(range(ghost_pop), ghost_pop)
    groups = []
    bracket = {}
    ghosts = {}
    for i in range(pac_pop):
        while len(ghosts) < 4:
            # if no ghosts left, reshuffle the list. Ghosts can be repeated as fitness is avg over games played
            if not shuffled:
                shuffled = random.sample(range(ghost_pop), ghost_pop)
            key = shuffled.pop()
            ghosts[key] = ghost_networks[key]["network"]
        # Store index as key for retrieval later. Assume network lists wont be altered later
        bracket["ghosts"] = ghosts
        bracket["pacman"] = (i, pacman_networks[i]["network"])
        groups.append(bracket)
        # reset for next iteration
        bracket = {}
        ghosts = {}
    return groups
