

import pygame, time

class timer:

	def __init__(self, screen):

		self.screen = screen

        self.centerx = self.screen.get_size()[0]/2
        self.centery = self.screen.get_size()[1]/2
        self.center = (self.centerx, self.centery)

        self.largeFont = pygame.font.Font(None, 72)

	def update(self):

		return

class stopwatch:

	def __init__(self, screen):

		self.screen = screen

        self.centerx = self.screen.get_size()[0]/2
        self.centery = self.screen.get_size()[1]/2
        self.center = (self.centerx, self.centery)

        self.largeFont = pygame.font.Font(None, 72)

    def start(self):

    	self.startTime = time.time()
    	self.elapsedTime = 0



	def update(self):



		return

	def showTime(self):

		

		return
