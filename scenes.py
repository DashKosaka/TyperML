# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 00:40:38 2018

@author: dashk
"""
import pygame, time
import typer as ty
from pygame.locals import *

##### Constants #####

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

RED = (255, 0, 0)
LIGHT_RED = (255, 150, 150)

GREEN = (0, 255, 0)
LIGHT_GREEN = (150, 255, 150)

BLUE = (0, 0, 255)
LIGHT_BLUE = (150, 150, 255)

##### Helpers #####

class Scenes:
    
    def __init__(self, screen):
        
        self.screen = screen
        self.centerx = self.screen.get_size()[0]/2
        self.centery = self.screen.get_size()[1]/2
        self.center = (self.centerx, self.centery)

        self.background = pygame.Surface(self.screen.get_size())

        self.largeFont = pygame.font.Font(None, 72)

    def finished(self):

        # Text
        font = pygame.font.Font(None, 72)
        finishedText = font.render('FINISHED!', 1, BLACK)

        # Position
        pos = finishedText.get_rect()
        pos.centerx = self.centerx

        # Background
        back = self.background.convert()
        back.fill(LIGHT_GREEN)    
        back.blit(finishedText, pos)
        
        self.screen.blit(back, (0, 0))
        pygame.display.flip()

    def _fill(self, color):
        back = self.background.convert()
        back.fill(color)
        self.screen.blit(back, (0, 0))
        pygame.display.flip()

    def countdown(self, count=5):

        countdown = ''

        self._fill(RED)

        for i in range(count):

            countdown += str(count-i) + '...'
            countText = self.largeFont.render(countdown, 1, (BLACK))

            self.screen.blit(countText, (0, 0))
            pygame.display.flip()

            time.sleep(1)

        countdown += 'GO!'
        countText = self.largeFont.render(countdown, 1, (BLACK))

        self._fill(GREEN)
        self.screen.blit(countText, countText.get_rect())
        pygame.display.flip()

        time.sleep(1)

        return

    def input(self, prompt=''):

        # Text
        promptText = self.largeFont.render(prompt, 1, (BLACK))

        # Position
        promptRect = promptText.get_rect()
        promptRect.centery = self.centery

        # Background
        back = self.background.convert()
        back.fill(LIGHT_RED)
        back.blit(promptText, promptRect)

        self.screen.blit(back, (0, 0))
        pygame.display.flip()

        ret = ''
        done = False

        inputText = self.largeFont.render(ret, 1, (BLACK))
        inputRect = inputText.get_rect()

        inputRect.midleft = promptRect.midright

        while(not done):

            for evt in pygame.event.get():

                if(evt.type == QUIT):return
                if(evt.type == KEYDOWN):

                    if(evt.key == K_RETURN):
                        done = True
                        break

                    elif(evt.unicode.isprintable()):

                        ret += evt.unicode
    
                        inputText = self.largeFont.render(ret, 1, (BLACK))
                        inputRect = inputText.get_rect()
                        inputRect.midleft = promptRect.midright

                        self.screen.blit(inputText, inputRect)
                        pygame.display.flip()

        return ret

    def stats(self):

        return

    def gameMode(self):

        return mode    

