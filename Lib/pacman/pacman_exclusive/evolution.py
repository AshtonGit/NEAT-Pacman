import neat
from Lib.pacman.pacman_exclusive.game import Game


# Only run as a demon thread. This ends the program window if pygame closed
# Run as a demon so that if program closed by other sources the thread is ended.



def eval_genomes(genomes, configuration, view):

    networks = []
    for i in range(len(genomes)):
        networks.append(neat.nn.FeedForwardNetwork.create(genomes[i][1], configuration))

    for n in range(len(networks)):
        # Genomes prowess in playing game of Pacman is direct indicator of its fitness
        fitness = play_game(networks[n], view)
        genomes[n][1].fitness = fitness


def play_game(network, view):
    game = Game(network)
    view.set_game(game)
    fitness = game.play_game()
    return fitness

