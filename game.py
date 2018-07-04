# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 21:01:19 2018

@author: dashk
"""
import pygame, random, time
import typer as ty
import scenes as sc
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

# http://www.pygame.org/pcr/text_rect/index.php
class TextRectException:
    def __init__(self, message = None):
        self.message = message
    def __str__(self):
        return self.message

def render_textrect(string, font, rect, text_color, background_color, justification=0):
    """Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Takes the following arguments:

    string - the text you wish to render. \n begins a new line.
    font - a Font object
    rect - a rectstyle giving the size of the surface requested.
    text_color - a three-byte tuple of the rgb value of the
                 text color. ex (0, 0, 0) = BLACK
    background_color - a three-byte tuple of the rgb value of the surface.
    justification - 0 (default) left-justified
                    1 horizontally centered
                    2 right-justified

    Returns the following values:

    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
    """

    import pygame
    
    final_lines = []

    requested_lines = string.splitlines()

    # Create a series of lines that will fit on the provided
    # rectangle.

    for requested_line in requested_lines:
        if font.size(requested_line)[0] > rect.width:
            words = requested_line.split(' ')
            # if any of our words are too long to fit, return.
            for word in words:
                if font.size(word)[0] >= rect.width:
                    raise TextRectException#, "The word " + word + " is too long to fit in the rect passed."
            # Start a new line
            accumulated_line = ""
            for word in words:
                test_line = accumulated_line + word + " "
                # Build the line while the words fit.    
                if font.size(test_line)[0] < rect.width:
                    accumulated_line = test_line 
                else: 
                    final_lines.append(accumulated_line) 
                    accumulated_line = word + " " 
            final_lines.append(accumulated_line)
        else: 
            final_lines.append(requested_line) 

    # Let's try to write the text out on the surface.

    surface = pygame.Surface(rect.size) 
    surface.fill(background_color) 

    accumulated_height = 0 
    for line in final_lines: 
        if accumulated_height + font.size(line)[1] >= rect.height:
            raise TextRectException#, "Once word-wrapped, the text string was too tall to fit in the rect."
        if line != "":
            tempsurface = font.render(line, 1, text_color)
            if justification == 0:
                surface.blit(tempsurface, (0, accumulated_height))
            elif justification == 1:
                surface.blit(tempsurface, ((rect.width - tempsurface.get_width()) / 2, accumulated_height))
            elif justification == 2:
                surface.blit(tempsurface, (rect.width - tempsurface.get_width(), accumulated_height))
            else:
                raise TextRectException#, "Invalid justification argument: " + str(justification)
        accumulated_height += font.size(line)[1]

    return surface


##### Main #####

def regular():
    # User set
    userName = input('What user are you: ').lower()

    numWords = input('How long should the passage be: ')
    try:numWords = int(numWords)
    except:numWords = random.randint(10, 25)

    # Initialize
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption('Typer Helper')

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
    paragraphBox = render_textrect(paragraphString, font, textBox, BLACK, LIGHT_BLUE)
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
                        
                        userTextBox = render_textrect(userString, font, userRect, BLACK, LIGHT_BLUE)
                        screen.blit(userTextBox, userRect)
                        pygame.display.flip()
                    
#                        elif(evt.key == K_SPACE):
#                            printFlag = True
#                            char = ' '
#                        
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

                userTextBox = render_textrect(userString, font, userRect, BLACK, LIGHT_BLUE)
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

        
    # Save the data to user
    ty.saveStats(stats, STATS_DIR, userName)     

    sc.finished(screen)               
        
if __name__ == '__main__':

    regular()
        