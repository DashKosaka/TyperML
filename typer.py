# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 02:29:28 2018

@author: Dash

This program acts as a helper to improve a user's typing speed by typing
randomized sentences from the user's choice of texts. It uses a combination
of Markov Chains and past statistical data to form the next paragraph. When
a user finishes typing a paragraph, the program will save the words that the
user had the most trouble with.

The user must first
- Load in text into the text.txt file as plain-text
- Enter in user set parameters

The program will then
- Load the data from the stats file and text file
- Form a randomized markov chain using the text with bias from past statistics
- Display the paragraph it made up along with a countdown
- Let the user type the paragraph out in console and
    save the letter combinations that were mistyped (ex. ei/ie, de/ed, etc...)
    along with the whole word that was misspelled
- Save that information into the given stats file

Problems
- There is a lot of relative overhead for small words like "a", "of", "be",
    making their respected wpm lower than average
    Solution? - Add words to stats.json if a mistake was made by the user

"""
import numpy as np
import sys
import json
import time
import msvcrt
from markovChain import MarkovChain
##### User Set #####



##### Constants #####

TEXT_FILE = 'text.txt'
SAVE_FILE = 'stats.json'

AVERAGE_LENGTH = 5.1    # Average length of a word in English Language

BAD = [b'\x00', b'\xff']    

##### Read Past Stats #####

with open(SAVE_FILE) as f:
    data = json.load(f)

##### Initialize #####

generator = MarkovChain(TEXT_FILE, data)

##### Generate Text #####

paragraph = generator.newParagraph(5)
print('Sentence to be typed:\n')
print(generator.asString())

##### Helpers #####

def _backspace(typed):
    print('\b \b', end='', flush=True)
    return typed[:len(typed)-1]

##### Run the Trainer #####
    
# Event loop
for idx, word in enumerate(paragraph):

    typed = ''
    currMistakes = 0
    startTime = time.time()
    
    while(1):
        char = msvcrt.getch()
        
        if(char in BAD):continue
        elif(char == b'\x03'):sys.exit('Keyboard Interrupt!')
        elif(char == b'\x08' and len(typed) > 0):
            typed = _backspace(typed)
            continue

        char = char.decode('utf-8')
        
        print(char, end='', flush=True)
    
        if(word == typed and char == ' '):break

        typed += char
        
        if(word[:len(typed)] != typed):currMistakes += 1
        elif(word == typed and idx == (len(paragraph)-1)):break
    
    if(currMistakes == 0):continue
    
    wpm = (len(word) / AVERAGE_LENGTH) / ((time.time() - startTime) / 60)
    
    if(word not in data.keys()):
        avgTime = wpm
        mistakes = currMistakes
        occurrences = 0
    else:
        avgTime = (data[word]['wpm'] + wpm) / 2
        mistakes = (data[word]['mistakes'] + mistakes) / 2
        occurrences = data[word]['occurrences'] + 1
    
    data[word] = {'mistakes':mistakes, 'wpm':avgTime, 'occurrences':occurrences}

        
##### Save the Stats #####

# What kind of information needs to be saved?
# 1. The word where the error occurred
# 2. The severity(?) of the mistake:
    # - Time taken (wpm)
    # - Number of keystroke deviations
    
with open(SAVE_FILE, 'w') as f:
    json.dump(data, f)

















