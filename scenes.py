# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 00:40:38 2018

@author: dashk
"""
import pygame

##### Constants #####

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

GREEN = (0, 255, 0)
LIGHT_GREEN = (150, 255, 150)

BLUE = (0, 0, 255)
LIGHT_BLUE = (150, 150, 255)

##### Helpers #####

def finished(screen):

    # Text
    font = pygame.font.Font(None, 72)
    finishedText = font.render('FINISHED!', 1, (10, 10, 10))

    # Positi
    pos = finishedText.get_rect()
    pos.centerx = screen.get_size()[0] / 2

    # Background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(LIGHT_GREEN)    
    background.blit(finishedText, pos)
    
    screen.blit(background, (0, 0))
    pygame.display.flip()
    
def name():

    return name

def length():

    return length

def gameMode():

    return mode    
