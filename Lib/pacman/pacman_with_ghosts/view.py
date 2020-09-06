from datetime import datetime
import pygame


class View:

    def __init__(self, current_game=None):
        pygame.init()
        pygame.display.set_mode((540, 475))
        self.display = pygame.display
        self.surface = pygame.display.get_surface()
        self.tile_size = 20
        self.current_game = current_game

        #setup font
        self.font = pygame.font.SysFont("Arial.ttf", 25)
        #setup timer
        self.timer_started = False
        self.start_time = 0

    def update(self):
        game = self.current_game
        candy_size = self.tile_size / 5
        candy_offset = (self.tile_size - candy_size) / 2
        if game is not None:
            if not game.game_over:
                pacman = game.pacman
                ghosts = game.ghosts
                tiles = game.tiles
                self.surface.fill((10, 10, 10))

                for row in range(len(tiles)):
                    for tile in range(len(tiles[row])):
                        y = row * self.tile_size
                        x = tile * self.tile_size
                        if tiles[row][tile] == 2:
                            center_x = x + candy_offset
                            center_y = y + candy_offset
                            candy_rect = pygame.Rect(center_x, center_y, candy_size, candy_size)
                            pygame.draw.rect(self.surface, (0, 255, 255), candy_rect)
                        elif tiles[row][tile] == 1:
                            wall_rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                            pygame.draw.rect(self.surface, (0, 0, 255), wall_rect)

                # Render pacman and ghosts
                pos = pacman.position
                pacman_img = pacman.get_model()
                self.surface.blit(pacman_img, (pos[1] * self.tile_size, pos[0] * self.tile_size))

                for i in range(len(ghosts)):
                    ghost = ghosts[i]
                    pos = ghost.position
                    self.surface.blit(ghost.get_model(), (pos[1] * self.tile_size, pos[0] * self.tile_size))

                # draw timer in top left corner
                if not self.timer_started:
                    self.timer_started = True
                    self.start_time = datetime.now()
                time = (datetime.now() - self.start_time).seconds
                time_text = self.font.render("time: "+str(time),True, (255, 255, 255))
                self.surface.blit(time_text, (0 + (time_text.get_width() // 2), -5 + (time_text.get_height() // 2)) )

                # display fitness of pacman and each ghost in the bottom, below the game
                # text color matches ghosts color. Red->Blue->Yellow->Green
                # each fitness text surface has 108  pixels of space (540 / 5)
                center_x = 54
                fitness_header = self.font.render("Fitness", True, (255, 255, 255))
                self.surface.blit(fitness_header, (10, 420))
                fitness_text = self.font.render(str(pacman.fitness), True, (255, 255, 255))
                self.surface.blit(fitness_text, (center_x , 450))

                ghost_color = [(0,255,0), (255, 255, 0), (0, 150, 150), (255, 0, 0)]
                for i in range(len(ghosts)):
                    fitness_text = self.font.render(str(ghosts[i].fitness), True, ghost_color[i])
                    center_x += 108
                    self.surface.blit(fitness_text, (center_x, 450 ))

                self.display.flip()

    def set_game(self, game):
        self.current_game = game
        self.timer_started = False

