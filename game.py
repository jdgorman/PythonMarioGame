import pygame

from pygame.locals import *
from time import sleep


class Mario():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 60
        self.h = 95
        self.prev_x = 0
        self.prev_y = 0
        self.yVel = 0
        self.image_right_list = [pygame.image.load("mario0.png"),
                                 pygame.image.load("mario1.png"),
                                 pygame.image.load("mario2.png"),
                                 pygame.image.load("mario3.png"),
                                 pygame.image.load("mario4.png")]
        self.image_left_list = [pygame.transform.flip(image, True, False) for image in self.image_right_list]
        self.image_index = 0
        self.off_ground_count = 0
        self.is_moving = False
        self.direction = "right"

    def jump(self):
        self.yVel = -20

    def update(self):
        # Gravity
        self.yVel = self.yVel + 1
        self.y = self.y + self.yVel

        # Floor bounds
        if self.y > 360:
            self.yVel = 0
            self.off_ground_count = 0
            self.y = 360

        # Value used to track Mario's jump height
        self.off_ground_count = self.off_ground_count + 1

        # Check if Mario is moving left or right for flipping image
        keys = pygame.key.get_pressed()
        if keys[K_LEFT] or keys[K_a]:
            self.is_moving = True
            self.direction = "left"
        elif keys[K_RIGHT] or keys[K_d]:
            self.is_moving = True
            self.direction = "right"
        else:
            self.is_moving = False

        # Update the image based on the direction
        if self.direction == "right":
            image_list = self.image_right_list
        else:
            image_list = self.image_left_list

        # Update the image_index to cycle through the images only when Mario is moving
        if self.is_moving:
            self.image_index = (self.image_index + 1) % len(image_list)
            self.image = image_list[self.image_index]
        else:
            # If Mario is not moving, display a stationary image
            self.image = image_list[0]

    # Store previous position to handle collisions
    def remember_state(self):
        self.prev_x = self.x
        self.prev_y = self.y

    # Keeps Mario out of tube bounds
    def snap_out(self, sprite):
        self.sprite = sprite
        if (self.x + self.w > self.sprite.x) and (self.prev_x + self.w <= self.sprite.x):
            self.x = self.sprite.x - self.w - 2
        elif (self.x < self.sprite.x + self.sprite.w) and (self.prev_x >= self.sprite.x + self.sprite.w):
            self.x = self.sprite.x + self.sprite.w
        elif (self.y + self.h >= self.sprite.y) and (self.prev_y + self.h < self.sprite.y):
            self.y = self.sprite.y - self.h - 2
            self.off_ground_count = 0
            self.yVel = 0


class Fireball():
    def __init__(self, x, y, x_vel=15):
        self.x = x
        self.y = y
        self.w = 47
        self.h = 47
        self.xVel = x_vel
        self.yVel = -12
        self.image = pygame.image.load("fireball.png")
        self.off_ground_count = 0

    def update(self):
        # Fireball motion
        self.x = self.x + self.xVel
        self.yVel = self.yVel + 1
        self.y = self.y + self.yVel

        # Floor bounds
        if self.y > 413:
            self.yVel = -10
            self.off_ground_count = 0
            self.y = 413

        # Used to track firball's height from ground
        self.off_ground_count = self.off_ground_count + 1


class Tube():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 55
        self.h = 400
        self.image = pygame.image.load("tube.png")

    def update(self):
        pass


class Goomba():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 99
        self.h = 118
        self.image = pygame.image.load("goomba.png")
        self.moving_right = True
        self.dead = False

    def update(self):
        if not self.dead:
            if self.moving_right:
                self.x = self.x + 3
            else:
                self.x = self.x - 3
            if self.x > 550:
                self.moving_right = False
            if self.x < 350:
                self.moving_right = True
        else:
            self.image = pygame.image.load("img.png")


class Model():
    def __init__(self):
        self.sprites = []

        self.mario = Mario(50, 360)
        self.sprites.append(self.mario)

        self.tube1 = Tube(200, 350)
        self.sprites.append(self.tube1)

        self.tube2 = Tube(700, 350)
        self.sprites.append(self.tube2)

        self.goomba = Goomba(300, 350)
        self.sprites.append(self.goomba)

        self.fireballs = []

    def add_fireball(self):
        fireball_x = self.mario.x
        fireball_y = self.mario.y
        fireball_direction = self.mario.direction

        # Determine which direction to throw fireball based on the direction Mario is facing
        if fireball_direction == "left":
            self.fireball = Fireball(fireball_x, fireball_y, x_vel=-15)
        else:
            self.fireball = Fireball(fireball_x, fireball_y)

        self.fireballs.append(self.fireball)

    def update(self):
        for sprite in self.sprites:
            sprite.update()
            # Handle collision with tubes
            if does_collide(self.mario.x, self.mario.y, self.mario.w, self.mario.h, self.tube1.x, self.tube1.y,
                            self.tube1.w,
                            self.tube1.h):
                self.mario.snap_out(self.tube1)
            if does_collide(self.mario.x, self.mario.y, self.mario.w, self.mario.h, self.tube2.x, self.tube2.y,
                            self.tube2.w,
                            self.tube2.h):
                self.mario.snap_out(self.tube2)

        for fireball in self.fireballs:
            fireball.update()
            # Handle fireball collision with goomba
            if does_collide(self.fireball.x, self.fireball.y, self.fireball.w, self.fireball.h,
                            self.goomba.x, self.goomba.y, self.goomba.w, self.goomba.h):
                self.goomba.dead = True

    def remember_state(self):
        self.mario.remember_state();


# Method for detecting collision between two objects
def does_collide(x1, y1, w1, h1, x2, y2, w2, h2):
    if x1 + w1 < x2:
        return False
    if x1 > x2 + w2:
        return False
    if y1 + h1 < y2:
        return False
    if y1 > y2 + h2:
        return False
    return True


class View():
    def __init__(self, model):
        screen_size = (1024, 560)
        self.screen = pygame.display.set_mode(screen_size, 20)
        self.backdrop = pygame.image.load("backdrop.png")
        self.model = model
        self.model.rect = self.backdrop.get_rect()

    def update(self):
        self.screen.fill([0, 100, 200])
        self.screen.blit(self.backdrop, self.model.rect)

        for sprite in self.model.sprites:
            self.screen.blit(sprite.image, (sprite.x, sprite.y))

        for fireball in self.model.fireballs:
            self.screen.blit(fireball.image, (fireball.x, fireball.y))

        pygame.display.flip()


class Controller():
    def __init__(self, model):
        self.model = model
        self.keep_going = True
        self.enableFireball = False

    def update(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.keep_going = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.keep_going = False
            elif event.type == KEYUP:
                if event.key == K_LCTRL or event.key == K_RCTRL:
                    self.enableFireball = True
        self.model.remember_state()
        keys = pygame.key.get_pressed()
        if keys[K_LEFT] or keys[K_a]:
            self.model.mario.x -= 7
        if keys[K_RIGHT] or keys[K_d]:
            self.model.mario.x += 7
        if keys[K_SPACE] and self.model.mario.off_ground_count < 3:
            self.model.mario.jump()
        if self.enableFireball:
            self.model.add_fireball()
            self.enableFireball = False


# Initialize Pygame
print("Use the arrow keys to move. Press Esc to quit.")
pygame.init()

# Set the window title
pygame.display.set_caption("Super Mario!")

# Create model, view, and controller objects
m = Model()
v = View(m)
c = Controller(m)

# Game loop
while c.keep_going:
    c.update()
    m.update()
    v.update()
    sleep(0.04)
print("Goodbye")
