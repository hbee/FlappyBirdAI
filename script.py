import os
import random
import time
import pygame
import neat


pygame.font.init()

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 800

BIRD_IMAGES = [
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))
]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
SCORE_FONT = pygame.font.SysFont("comicsans", 50)

class Bird:
    IMGS = BIRD_IMAGES
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 10

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        d = self.vel*self.tick_count + 1.5*self.tick_count**2
        d = 16 if d >= 16 else d
        if d < 0:
            d -= 2
        self.y += d
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, window):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[0]
            self.img_count = self.ANIMATION_TIME*2

        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rectangle = rotated_img.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center
        )

        window.blit(rotated_img, new_rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200
    VELOCITY = 5

    def __init__(self, x):
        self.x = x
        self.tip_top_pipe = 0
        self.onset_top_pipe = 0
        self.tip_bottom_pipe = 0
        self.TOP_PIPE = pygame.transform.flip(
            PIPE_IMG, False, True
        )
        self.BOTTOM_PIPE = PIPE_IMG
        self.passed = False
        self.set_height()

    def set_height(self):
        self.tip_top_pipe = random.randrange(50, 450)
        self.onset_top_pipe = self.tip_top_pipe - self.TOP_PIPE.get_height()
        self.tip_bottom_pipe = self.tip_top_pipe + self.GAP

    def move(self):
        self.x -= self.VELOCITY

    def draw(self, window):
        window.blit(self.TOP_PIPE, (self.x, self.onset_top_pipe))
        window.blit(self.BOTTOM_PIPE, (self.x, self.tip_bottom_pipe))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.TOP_PIPE)
        bottom_mask = pygame.mask.from_surface(self.BOTTOM_PIPE)
        top_offset = (self.x - bird.x, self.onset_top_pipe - round(bird.y))
        bottom_offset = (self.x - bird.x, self.tip_bottom_pipe - round(bird.y))
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)
        if None not in (b_point, t_point):
            return True
        return False


class Base:
    VELOCITY = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, window):
        window.blit(self.IMG, (self.x1, self.y))
        window.blit(self.IMG, (self.x2, self.y))


def draw_window(win, bird, pipes, base, score):
    win.blit(BG_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(win)
    text = SCORE_FONT.render("Score : " + str(score), 1, (255, 255, 255))
    win.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 10))
    base.draw(win)
    bird.draw(win)
    pygame.display.update()


def main():
    clock = pygame.time.Clock()
    bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    score = 0

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        # bird.move()
        to_remove = []
        add_pipe = False
        for pipe in pipes:
            if pipe.collide(bird):
                pass
            if pipe.x + pipe.TOP_PIPE.get_width() < 0:
                to_remove.append(pipe)
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(650))
        for r in to_remove:
            pipes.remove(r)
        if bird.y + bird.img.get_height() >= 730:
            pass
        base.move()
        draw_window(win, bird, pipes, base, score)
    pygame.quit()
    quit()


main()

