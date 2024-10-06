# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 21:01:19 2018

@author: dashk
"""
import pygame, random, time
import typer as ty
from scenes import Scenes
from pygame.locals import *
from markovChain import MarkovChain


##### Constants #####

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

GREEN = (0, 255, 0)
LIGHT_GREEN = (150, 255, 150)

BLUE = (0, 0, 255)
LIGHT_BLUE = (150, 150, 255)

SIZE = (1250, 500)

TEXT_DIR = './text/'
SAVE_FILE = 'stats.json'
STATS_DIR = './users/'

AVERAGE_LENGTH = 5.1    # Average length of a word in English Language
COUNTDOWN = 5

##### Helpers #####



##### Main #####

def regular():


    # Initialize
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption('Typer Helper')
    sc = Scenes(screen)

    # User set
    userName = sc.input('What user are you: ').lower()

    numWords = sc.input('How long should the passage be: ')
    try:numWords = int(numWords)
    except:numWords = random.randint(10, 25)

    sc.countdown()

    # Background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(LIGHT_BLUE)
    
    # Text
    stats = ty.getProfile(STATS_DIR, userName)
    data, history = stats['words'], stats['wpm']
    generator = MarkovChain(TEXT_DIR, data)
    paragraph = generator.newParagraph(numWords)
    paragraphString = generator.asString()

    # Display paragraph to be typed
    font = pygame.font.Font(None, 36)
    text = font.render('', 1, (10, 10, 10))
    textpos = text.get_rect()
    textBox = pygame.Rect(0, 0, *SIZE)
    paragraphBox = ty.render_textrect(paragraphString, font, textBox, BLACK, LIGHT_BLUE)
    background.blit(paragraphBox, textpos)
    
    # Blit to screen
    screen.blit(background, (0, 0))
    pygame.display.flip()
    
    # Event loop (game start)
    revisited = {}
    wrongWords = {}

    userString = ''
    userRect = pygame.Rect(0, SIZE[1]/2, SIZE[0], SIZE[1]/2)
    for idx, word in enumerate(paragraph):

        userWord = ''
        currMistakes = 0
        startTime = time.time()
        nextWord = False

        while(not nextWord):
            # Get keypress
            printFlag = False
            for evt in pygame.event.get():
            
                if(evt.type == QUIT):return
                elif(evt.type == KEYDOWN):

                    if(idx == 0 and userWord == ''):totalTime = startTime = time.time()

                    if(evt.key == K_BACKSPACE):
                        userWord = userWord[:len(userWord)-1]
                        userString = userString[:len(userString)-1]
                        
                        userTextBox = ty.render_textrect(userString, font, userRect, BLACK, LIGHT_BLUE)
                        screen.blit(userTextBox, userRect)
                        pygame.display.flip()
                   
                    elif(evt.unicode.isprintable()):
                        # Check for mistake
                        if(len(userWord) > len(word)):
                            currMistakes += 1
                            break

                        printFlag = True
                        char = evt.unicode
                    break

            if(printFlag):
                if(word == userWord and char == ' '):
                    userString += ' '
                    nextWord = True
                    break

                userWord += evt.unicode
                userString += evt.unicode

                userTextBox = ty.render_textrect(userString, font, userRect, BLACK, LIGHT_BLUE)
                screen.blit(userTextBox, userRect)
                pygame.display.flip()

                # Mistake has been made
                if(word[:len(userWord)] != userWord):currMistakes += 1
                # Paragraph is finished
                elif(word == userWord and idx == (len(paragraph)-1)):
                    nextWord = True
                    break
                


        # Save the stats for the word if a mistake has been made
        if((currMistakes == 0) and (word not in generator.revisited)):continue

        wpm = (len(word) / AVERAGE_LENGTH) / ((time.time() - startTime) / 60)

        # Update the dictionaries
        if(word not in data.keys()):
            avgTime = wpm
            avgMistakes = currMistakes
            totalOccurrences = 1
            lifetime = wpm
        else:
            avgTime = (data[word]['biased'] + wpm) / 2
            avgMistakes = (data[word]['mistakes'] + currMistakes) / 2
            totalOccurrences = data[word]['occurrences'] + 1
            lifetime = ((data[word]['lifetime'] * data[word]['occurrences']) + wpm) / totalOccurrences
        
        if(word in generator.revisited):
            revisited[word] = {'deltaMistakes':(currMistakes-data[word]['mistakes']), 'deltaWPM':(wpm-data[word]['biased'])}
        else:
            wrongWords[word] = {'mistakes':currMistakes, 'wpm':wpm}
        
        data[word] = {'mistakes':avgMistakes, 'biased':avgTime, 
                    'lifetime':wpm, 'occurrences':totalOccurrences}

    totalWPM = (len(paragraphString) / AVERAGE_LENGTH) / ((time.time() - totalTime) / 60)
        
    # Save the data to user
    ty.saveStats(stats, STATS_DIR, userName)     

    sc.finished()               
    
    sc.message('WPM: ' + str(totalWPM))
        
if __name__ == '__main__':
    
#    menu = 
    regular()
        
    # Add
    # - Timed Mode
    # - Symbol Mode
    # - Horde Mode
