from .game import *
from tensorflow.keras import layers, Model
from tensorflow import convert_to_tensor

class NNModel():
    def __init__(self):
        n_params = 6   # y_dist_targ, x_dist_targ, angle, vx, vy, y_dist_floor 
        n_hidden = 2
        n_output = 3   # up, left, right
        inputs = layers.Input(shape=(n_params,))
        common = layers.Dense(n_hidden, activation='relu')(inputs)
        action = layers.Dense(n_output, activation='softmax')(common)
        self.model = Model(inputs=inputs, outputs=action)
        self.model.compile()
        
class TrainablePlayer(Spaceship, NNModel):
    def __init__(self, screen):
        Spaceship.__init__(self, screen)
        NNModel.__init__(self)

    
    def get_input_variables(self, target):
        y_dist_targ = (self.pos.y - target.pos.y) #/ self.y_boundaries[1]
        x_dist_targ = (self.pos.x - target.pos.x) #/ self.x_boundaries[1]
        angle = self.rotation_angle #/ 90
        vx = self.velocity.x #/ 500
        vy = self.velocity.y #/ 500
        y_dist_floor = (self.y_boundaries[1] - self.pos.y) #/ self.y_boundaries[1]
        
        input_vars = [y_dist_targ, x_dist_targ, angle, vx, vy, y_dist_floor]
        return convert_to_tensor([input_vars], dtype="float32")

    def get_moving_commands(self, target): 
        input_vars = self.get_input_variables(target)
        return self.model(input_vars).numpy()[0]
        


class ModelTraining(SpaceshipGame):

    def __init__(self):
        self.threshold_command = 0.33

    def get_target_training(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 60)
        self.running = True
        self.start_time = pygame.time.get_ticks()
        self.time_finished = False
        
        number_players = 30
        players = [TrainablePlayer(self.screen) for _ in range(number_players)]
        target = Target(self.screen, players[0].pos.x, players[0].pos.y-SCREEN_SIZE[1]/0.8)

        dt = 0
        while self.running:
            self.check_for_quit()
            
            self.set_backgroud()

            players_alive = [player for player in players if player.alive]
            for player in players_alive:
                up, left, right = player.get_moving_commands(target) > self.threshold_command
                #up,left,right = random.random() > 0.5, random.random() > 0.5, random.random() > 0.5 
                player.move(up=up,
                            right=right,
                            left=left,
                            dt=dt)
                player.draw()
                target.draw()
                if self.check_got_target(player, target):  # The same player can "get" the target multiple times. Shouldn't reward every single time. Or should?
                    print("Got target!!")

                self.set_clock(time_max=5)
                if self.time_finished:   # Have to work on the timer for the training
                    self.running = False

            pygame.display.flip()
            #self.saveframes("path/to/save")
            
            # limits FPS to 60. dt is delta time in seconds since last frame, used for framerate-independent physics.
            dt = self.clock.tick(60) / 1000
        
        pygame.quit()