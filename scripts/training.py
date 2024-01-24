from .game import *

class ModelTraining(SpaceshipGame):

    def __init__(self):
        pass

    def get_target_training(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 60)
        self.running = True
        self.start_time = pygame.time.get_ticks()
        self.time_finished = False
        
        number_players = 10
        players = [Spaceship(self.screen) for _ in range(number_players)]
        target = Target(self.screen, players[0].pos.x, players[0].pos.y-SCREEN_SIZE[1]/0.8)

        dt = 0
        while self.running:
            self.check_for_quit()
            
            self.set_backgroud()

            players_alive = [player for player in players if player.alive]
            for player in players_alive:
                
                player.move(up=random.random() > 0.6,
                            right=random.random() > 0.7,
                            left=random.random() > 0.7,
                            dt=dt)
                player.draw()
                target.draw()
                if self.check_got_target(player, target):  # The same player can "get" the target multiple times. Shouldn't reward every single time. Or should?
                    print("Got target!!")

                #self.set_clock(time_max=10)
                #if self.time_finished:   # Have to work on the timer for the training
                #    self.handle_timeoff(player, target)

            pygame.display.flip()
            #self.saveframes("path/to/save")
            
            # limits FPS to 60. dt is delta time in seconds since last frame, used for framerate-independent physics.
            dt = self.clock.tick(60) / 1000
        
        pygame.quit()