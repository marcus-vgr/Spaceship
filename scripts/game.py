import pygame
from numpy import cos, sin, pi

SCREEN_SIZE = (1280, 720)
SPACECHIP_SIZE = (80,100)
FLOOR_SIZE = (SCREEN_SIZE[0]*1.2, 100)
PLATFORM_SIZE = (SCREEN_SIZE[0]/3, 200)
BLIT_SKY = (0,0)
BLIT_FLOOR = (0, SCREEN_SIZE[1]-FLOOR_SIZE[1])
BLIT_PLATFORM = (SCREEN_SIZE[0]/3, SCREEN_SIZE[1] - PLATFORM_SIZE[1] + 50)


class Spaceship():
    def __init__(self, screen):
        self.screen = screen
        self.image = pygame.image.load("FiguresGame/spaceship.png")
        self.image = pygame.transform.scale(self.image, SPACECHIP_SIZE)

        self.x_boundaries = [-SPACECHIP_SIZE[1]*0.2, self.screen.get_width()-SPACECHIP_SIZE[1]*0.6]
        self.y_boundaries = [0, self.screen.get_height() - FLOOR_SIZE[1] - SPACECHIP_SIZE[1]*0.6]
        self.pos = pygame.Vector2(screen.get_width()/2 - SPACECHIP_SIZE[0]*0.5, self.y_boundaries[1])
        self.velocity = pygame.Vector2(0, 0)
        self.rotation_angle = 0  # Keep track of the angle of the spaceship
        
        # Parameters of the game for each movement
        self.gravity = 200
        self.boost = 800
        self.angle_torque = 5 
    
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
        self.make_boundary_corrections()

        self.rotated_image = pygame.transform.rotate(self.image, self.rotation_angle) #We can not alter the original image
        self.screen.blit(self.rotated_image, self.pos)
        
    
    #### TODO: destroy spaceship if colliding in the floor. Should be able to touch floor only with a minimum velocity, angle, and inside the platform
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
        
        ### Working on boundaries at the y-axis
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
        self.running = True
        
        player = Spaceship(self.screen)

        dt = 0
        while self.running:
            self.check_for_quit()
            
            self.set_backgroud()
            keys = pygame.key.get_pressed()
            player.move(up=keys[pygame.K_w],
                        right=keys[pygame.K_d],
                        left=keys[pygame.K_a],
                        dt=dt)

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
    
    
    def check_for_quit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        
    