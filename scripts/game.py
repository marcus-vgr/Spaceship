import pygame
from numpy import cos, sin, pi, random
import time

SCREEN_SIZE = (1280, 720)
SPACECHIP_SIZE = (60,75)
EXPLOSION_SIZE = (100,100)
FLOOR_SIZE = (SCREEN_SIZE[0]*1.2, 100)
PLATFORM_SIZE = (SCREEN_SIZE[0]/3, 200)
TARGET_SIZE = (60,60)
BLIT_SKY = (0,0)
BLIT_FLOOR = (0, SCREEN_SIZE[1]-FLOOR_SIZE[1])
BLIT_PLATFORM = (SCREEN_SIZE[0]/3, SCREEN_SIZE[1] - PLATFORM_SIZE[1] + 50)
MINIMUM_DISTANCE_TARGET = 30

class Target():
    def __init__(self, screen):
        self.screen = screen
        self.image = pygame.image.load("FiguresGame/target.png")
        self.image = pygame.transform.scale(self.image, TARGET_SIZE)

        self.x_max = self.screen.get_width()*0.9
        self.y_max = self.screen.get_height() - FLOOR_SIZE[1] - SPACECHIP_SIZE[1]*0.6 # Need to adjust y_max later to dont get the target before landing...
        self.pos = pygame.Vector2(0, 0)
        self.pos.x = random.uniform(30, self.x_max)
        self.pos.y = random.uniform(30, self.y_max) 

        self.landing_target = False
        self.counter = 0
        self.number_targets = 1 # Number of targets to collect behore landing

    def draw(self):
        self.screen.blit(self.image, self.pos) 

    def change_position(self):
        if self.counter < self.number_targets-1:
            self.pos.x = random.uniform(30, self.x_max)
            self.pos.y = random.uniform(30, self.y_max) # Need to adjust y_max later to dont get the target
            self.counter += 1
        else:

            self.pos.x = random.uniform( (BLIT_PLATFORM[0] + PLATFORM_SIZE[0]*0.2), (BLIT_PLATFORM[0] + PLATFORM_SIZE[0]*0.8) )
            self.pos.y = self.y_max
            self.landing_target = True

    def reset(self):
        self.pos.x = random.uniform(30, self.x_max)
        self.pos.y = random.uniform(30, self.y_max) 
        
        self.landing_target = False
        self.counter = 0


class Spaceship():
    def __init__(self, screen):
        self.screen = screen
        self.image = pygame.image.load("FiguresGame/spaceship.png")
        self.image = pygame.transform.scale(self.image, SPACECHIP_SIZE)
        self.image_explosion = pygame.image.load("FiguresGame/explosion.png")
        self.image_explosion = pygame.transform.scale(self.image_explosion, EXPLOSION_SIZE)

        self.x_boundaries = [-SPACECHIP_SIZE[1]*0.2, self.screen.get_width()-SPACECHIP_SIZE[1]*0.6]
        self.y_boundaries = [0, self.screen.get_height() - FLOOR_SIZE[1] - SPACECHIP_SIZE[1]*0.6]
        self.pos = pygame.Vector2(self.screen.get_width()/2 - SPACECHIP_SIZE[0]*0.5, self.y_boundaries[1])
        self.velocity = pygame.Vector2(0, 0)
        self.rotation_angle = 0  # Keep track of the angle of the spaceship
        self.alive = True
        self.explosion_time = None
        self.landed = False

        # Parameters of the game for each movement
        self.gravity = 200
        self.boost = 800
        self.angle_torque = 5 
        self.max_velocity_landing = 100
    
    def reset(self):
        self.pos = pygame.Vector2(self.screen.get_width()/2 - SPACECHIP_SIZE[0]*0.5, self.y_boundaries[1])
        self.velocity = pygame.Vector2(0, 0)
        self.rotation_angle = 0  # Keep track of the angle of the spaceship
        self.alive = True
        self.explosion_time = None
        self.landed = False

    def draw(self):
        if self.alive:
            self.rotated_image = pygame.transform.rotate(self.image, self.rotation_angle) #We can not alter the original image
            self.screen.blit(self.rotated_image, self.pos)
        else:
            self.screen.blit(self.image_explosion, self.pos)
    
    def move(self, up=False, right=False, left=False, dt=0):
        
        if right:  # Right-left just change the angle of the spaceship
            self.rotation_angle -= self.angle_torque
        if left: 
            self.rotation_angle += self.angle_torque
        
        if up:  # If pressing up we give a boost -- later add some fuel comsuption here...
            self.velocity.x += self.boost * cos(self.rotation_angle*pi/180 + pi/2) * dt
            self.velocity.y += (-self.boost * sin(self.rotation_angle*pi/180 + pi/2) * dt)
        else:   # If not accelarating, the spaceship falls because of gravity
            self.velocity.y += self.gravity * dt      
        
        self.pos += self.velocity * dt        
        self.check_explosion()
        self.make_boundary_corrections()
            
    
    def check_explosion(self):
        
        if self.pos.y >= self.y_boundaries[1]: # Check if we are in the floor
            if self.pos.x <= BLIT_PLATFORM[0] or self.pos.x >= (BLIT_PLATFORM[0]+PLATFORM_SIZE[0])*0.95: # Check if we are outside the platform
                self.alive = False
            elif self.velocity.magnitude() > self.max_velocity_landing or abs(self.rotation_angle) > self.angle_torque:
                self.alive = False
        
        if not self.alive:
            self.explosion_time = time.time() 
            
    def set_landing(self):
        self.landed = True
        self.landing_time = time.time()


    def make_boundary_corrections(self):
        
        ### Working on boundaries at the x-axis
        if self.pos.x <= self.x_boundaries[0]:
            self.pos.x = self.x_boundaries[0]
            if self.velocity.x < 0:
                self.velocity.x = 0
        if self.pos.x >= self.x_boundaries[1]:
            self.pos.x = self.x_boundaries[1]
            if self.velocity.x > 0:
                self.velocity.x = 0
        
        ### Working on boundaries at the y-axis.
        if self.pos.y <= self.y_boundaries[0]:
            self.pos.y = self.y_boundaries[0]
            self.velocity.y = 0
        if self.pos.y >= self.y_boundaries[1]:
            self.pos.y = self.y_boundaries[1]
            if self.velocity.y > 0:
                self.velocity.y = 0
        
        ### Not moving the spaceship horizontally if on-ground
        if abs(self.velocity.x) > 0 and self.pos.y >= self.y_boundaries[1]:
            self.velocity.x = 0
            


class SpaceshipGame():

    def __init__(self):
        pass

    def play(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 60)
        self.running = True
        
        player = Spaceship(self.screen)
        target = Target(self.screen)

        dt = 0
        while self.running:
            self.check_for_quit()
            
            self.set_backgroud()

            if player.alive:
                keys = pygame.key.get_pressed()
                player.move(up=keys[pygame.K_w],
                            right=keys[pygame.K_d],
                            left=keys[pygame.K_a],
                            dt=dt)
            else:
                self.handle_explosion(player, target)
            
            if not player.landed:
                    player.draw()
                    target.draw()
                    self.check_got_target(player, target)
            elif player.landed and player.alive:
                self.handle_newgame(player, target)

            pygame.display.flip()
            
            # limits FPS to 60. dt is delta time in seconds since last frame, used for framerate-independent physics.
            dt = self.clock.tick(60) / 1000
        
        pygame.quit()

    def set_backgroud(self):
        sky = pygame.image.load("FiguresGame/sky.jpg")
        sky = pygame.transform.scale(sky, SCREEN_SIZE)
        floor = pygame.image.load("FiguresGame/floor.png")
        floor = pygame.transform.scale(floor, FLOOR_SIZE)
        platform = pygame.image.load("FiguresGame/platform.png")
        platform = pygame.transform.scale(platform, PLATFORM_SIZE)        
        
        self.screen.blit(sky, BLIT_SKY)
        self.screen.blit(floor, BLIT_FLOOR)
        self.screen.blit(platform, BLIT_PLATFORM)
    
    def check_got_target(self, player, target): 
        
        if not target.landing_target:
            dist = player.pos.distance_to(target.pos)
            if dist <= MINIMUM_DISTANCE_TARGET:
                target.change_position()
        else:
            if abs(player.pos.y - target.pos.y) < 1e-6 and abs(player.pos.x - target.pos.x) < MINIMUM_DISTANCE_TARGET:
                player.set_landing()

    def handle_explosion(self, player, target):
        time_delay = 2 # time to reset game
        elapsed_time = time.time() - player.explosion_time
        if elapsed_time > time_delay:
            player.reset()
            target.reset()
        else:
            lose_img = self.font.render("You Lost!", True, (0,0,0))
            self.screen.blit(lose_img, (self.screen.get_width()/2.4, self.screen.get_height()/2))

    def handle_newgame(self, player, target):
        time_delay = 2 # time to reset game
        elapsed_time = time.time() - player.landing_time
        if elapsed_time > time_delay:
            player.reset()
            target.reset() 
        else:
            congratulation_img = self.font.render("Congratulations!", True, (0,0,0))
            self.screen.blit(congratulation_img, (self.screen.get_width()/2.8, self.screen.get_height()/2))
            
    def check_for_quit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        
    