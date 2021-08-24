import pygame
from disease_classes import Disease, Person, Location, circle_collide
import numpy as np
import pandas as pd

RED = (255, 100, 100)
BROWN = (210, 105, 30)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 128)
BLUE = (0, 0, 255)
GREY = (128, 128, 128)

POPULATION_SIZE = 200
WIDTH = 640
HEIGHT = 480
FPS = 30


screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.init()

population = []

for i in range(POPULATION_SIZE):
    p = Person()
    population.append(p)

coronavirus = Disease(percent=0.01, duration=10, death=0.01)

for p in population:
    coronavirus.infect(p)

"""
Sprite groups.
"""
all_sprites = pygame.sprite.Group(population)
ill = pygame.sprite.Group()
healthy = pygame.sprite.Group()
recovered = pygame.sprite.Group()

for sprite in all_sprites:
    if sprite.infected:
        ill.add(sprite)
    elif not sprite.infected:
        healthy.add(sprite)

clock_image = [pygame.image.load("images/clock/1.png"), pygame.image.load("images/clock/2.png"),
               pygame.image.load("images/clock/3.png"), pygame.image.load("images/clock/4.png"),
               pygame.image.load("images/clock/5.png"), pygame.image.load("images/clock/6.png"),
               pygame.image.load("images/clock/7.png"), pygame.image.load("images/clock/8.png"),
               pygame.image.load("images/clock/9.png"), pygame.image.load("images/clock/10.png"),
               pygame.image.load("images/clock/11.png"), pygame.image.load("images/clock/12.png")]

clock_count = 0
day_count = 1
frame_count = 1
graph_frame_count = 0

font = pygame.font.Font('freesansbold.ttf', 20)
graphing_data = {'S': np.repeat(0.00, 50), 'I': np.repeat(0.00, 50), 'R': np.repeat(0.00, 50)}
graph_data = pd.DataFrame(data=graphing_data)

running = True
while running:
    pygame.time.Clock().tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for p in population:
        previously_ill = []

        if p.infected:
            previously_ill.append(p)

        coronavirus.pass_day(p)

        if not p.infected and p in previously_ill:
            ill.remove(p)
            recovered.add(p)

        previously_ill.clear()

    all_sprites.update()

    hits = pygame.sprite.groupcollide(healthy, ill, False, False, collided=circle_collide)

    for healthy_individual in hits:
        healthy_individual.infect()
        healthy.remove(healthy_individual)
        ill.add(healthy_individual)

    screen.fill(BLACK)
    for sprite in all_sprites:
        sprite.draw()

    """
    Clock: Animation
    """
    if clock_count > 11:
        clock_count = 0
    screen.blit(clock_image[clock_count], (5, 5))
    clock_count += 1

    """
    Clock: Day Text
    """
    if frame_count > 30:
        day_count += 1
        frame_count = 1
    text = font.render('Day: {}'.format(day_count), True, WHITE)
    textRect = text.get_rect()
    textRect.x = 35
    textRect.y = 8
    screen.blit(text, textRect)
    frame_count += 1

    """
    Status Bars: S:I:R
    """
    percent_ill = len(ill) / len(all_sprites)
    percent_healthy = len(healthy) / len(all_sprites)
    percent_recovered = len(recovered) / len(all_sprites)

    pygame.draw.rect(screen, WHITE, (6, 40, 100, 10), 1)
    pygame.draw.rect(screen, RED, (6, 55, 100, 10), 1)
    pygame.draw.rect(screen, GREY, (6, 70, 100, 10), 1)

    pygame.draw.rect(screen, WHITE, (6, 40, 100 * percent_healthy, 10))
    pygame.draw.rect(screen, RED, (6, 55, 100 * percent_ill, 10))
    pygame.draw.rect(screen, GREY, (6, 70, 100 * percent_recovered, 10))

    """
    Updating graph_data
    """

    graph_data['S'][graph_frame_count] = percent_healthy
    graph_data['I'][graph_frame_count] = percent_ill
    graph_data['R'][graph_frame_count] = percent_recovered

    """
    Graph : S: I: R
    """
    top_left_x = 130
    top_left_y = 5
    bot_left_x = 130
    bot_left_y = 80

    # i = each row of graph
    for i in range(50):
        pygame.draw.line(screen, WHITE, (top_left_x+2*i, top_left_y), (bot_left_x+2*i, top_left_y + 75*graph_data['S'][i]), 2)
        pygame.draw.line(screen, RED, (top_left_x+2*i, top_left_y + 75*graph_data['S'][i]), (bot_left_x+2*i, top_left_y + 75*graph_data['S'][i] + 75*graph_data['I'][i]), 2)
        pygame.draw.line(screen, GREY, (top_left_x+2*i, (top_left_y + 75*graph_data['S'][i] + 75*graph_data['I'][i])), (bot_left_x+2*i, top_left_y + 75*graph_data['S'][i] + 75*graph_data['I'][i] + 75*graph_data['R'][i]), 2)

    if graph_frame_count < 49:
        graph_frame_count += 1
    else:
        graph_frame_count = 0

    pygame.display.flip()

pygame.quit()
