from .game import *
from tensorflow.keras import layers, Model
from tensorflow.keras.models import clone_model
from tensorflow.random import normal
from tensorflow import convert_to_tensor


class NNModel():
    def __init__(self, basemodel=None):
        if basemodel is None:
            n_params = 6   # y_dist_targ, x_dist_targ, angle, vx, vy, y_dist_floor 
            n_hidden = 2
            n_output = 3   # up, left, right
            inputs = layers.Input(shape=(n_params,), name='input1')
            common = layers.Dense(n_hidden, activation='relu', name='dense1')(inputs)
            action = layers.Dense(n_output, activation='softmax', name='dense2')(common)
            self.model = Model(inputs=inputs, outputs=action)
            self.model.compile()
        else:
            self.model = clone_model(basemodel)
            for layer in self.model.layers:
                weights = basemodel.get_layer(name=layer.name).get_weights()
                modified_weights = [w + normal(w.shape, stddev=0.01) for w in weights]
                layer.set_weights(modified_weights)
            self.model.compile()


class TrainablePlayer(Spaceship, NNModel):
    def __init__(self, screen, randomx=False, randomy=False, basemodel=None):
        Spaceship.__init__(self, screen)
        NNModel.__init__(self, basemodel)
        if randomx:
            self.pos.x = random.uniform(BLIT_PLATFORM[0], (BLIT_PLATFORM[0]+PLATFORM_SIZE[0])*0.95)
        if randomy:
            ymax = self.screen.get_height() - FLOOR_SIZE[1] - SPACECHIP_SIZE[1]*0.6
            self.pos.y = random.uniform(30, ymax)  

        self.score = 0  
    
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
        self.threshold_command = 0.4
        self.target_score = 40
        self.die_score = -5


    def get_target_training(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 60)
        self.start_time = pygame.time.get_ticks()
        self.time_finished = False
        
        max_number_generations = 4
        number_generations = 0
        number_players = 300
        number_players_evolute = 10
        self.players = [TrainablePlayer(self.screen, randomx=True) for _ in range(number_players)]
        self.get_target_training_run()        
        
        while number_generations < max_number_generations: 
            top_players = list( sorted(self.players, key=lambda x: x.score, reverse=True)[:number_players_evolute] ) 
            for i,player in enumerate(top_players):
                print(f"Player {i}: Score = {player.score}")
            print('===============================================')
            
            self.players = []   # Recreate players based on the top players
            for _ in range(number_players):
                evolute_idx = random.randint(0, number_players_evolute) # Select a random player to evolute from the top ones
                model = top_players[evolute_idx].model
                self.players.append( TrainablePlayer(self.screen, randomx=True, basemodel=model)  )
            
            self.get_target_training_run()
            number_generations += 1

        pygame.quit()

    def get_target_training_run(self):

        target = Target(self.screen)
        running = True
        dt = 0
        counter = 0
        max_counter = 2
        while running:
            self.check_for_quit()
            
            self.set_backgroud()

            players_alive = [player for player in self.players if player.alive]
            for player in players_alive:
                up, left, right = player.get_moving_commands(target) > self.threshold_command
                player.move(up=up,
                            right=right,
                            left=left,
                            dt=dt)
                player.draw()
                target.draw()
                if self.check_got_target(player, target):  # The same player can "get" the target multiple times. Shouldn't reward every single time. Or should?
                    player.score += self.target_score
                if not player.alive: # Died this movement
                    player.score += self.die_score

            self.set_clock(time_max=5)
            if self.time_finished:   # Have to work on the timer for the training
                counter += 1
                for player in self.players:
                    self.handle_timeoff(player, target, time_delay=0, randomx=True, randomy=False)
            
            pygame.display.flip()
            #self.saveframes("path/to/save")
            
            # limits FPS to 60. dt is delta time in seconds since last frame, used for framerate-independent physics.
            dt = self.clock.tick(60) / 1000
        
            if counter >= max_counter:
                running = False
