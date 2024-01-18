import pygame

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
        self.pos = pygame.Vector2(screen.get_width()/2 - SPACECHIP_SIZE[0]*0.5, screen.get_height()/2)

        self.x_boundaries = [-SPACECHIP_SIZE[1]*0.2, self.screen.get_width()-SPACECHIP_SIZE[1]*0.6]
        self.y_boundaries = [0, self.screen.get_height() - FLOOR_SIZE[1] - SPACECHIP_SIZE[1]*0.6]

    def move(self, up=False, down=False, right=False, left=False, dt=0):
        if up:
            self.pos.y -= 300 * dt # "Up" is going down in coordinates.
        if down:
            self.pos.y += 300 * dt        
        if right:
            self.pos.x += 300 * dt
        if left:
            self.pos.x -= 300 * dt
        self.check_coordinates()

        self.screen.blit(self.image, self.pos)

    def check_coordinates(self):
        if self.pos.x < self.x_boundaries[0]:
            self.pos.x = self.x_boundaries[0]
        if self.pos.x > self.x_boundaries[1]:
            self.pos.x = self.x_boundaries[1]
        if self.pos.y < self.y_boundaries[0]:
            self.pos.y = self.y_boundaries[0]
        if self.pos.y > self.y_boundaries[1]:
            self.pos.y = self.y_boundaries[1]
        
            


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
                        down=keys[pygame.K_s],
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
        
    