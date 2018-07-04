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
import sys, os, json, time, msvcrt, random
from markovChain import MarkovChain

##### Constants #####

BAD = [b'\x00', b'\xff', b'\xe0']    

##### Read Past Stats #####


def _makeProfile(path, name):
    cleanData = {'name':name, 'games':0, 'wpm':{'lifetime':0, 'recent':[], 'all':[]}, 'words':{}}
    
    with open(path, 'w') as f:
        json.dump(cleanData, f)

def getProfile(directory, userName):
    path = directory + userName + '.json'
    
    if(not os.path.isfile(path)):_makeProfile(path, userName)
    
    with open(path) as f:
        stats = json.load(f)
    
    return stats

##### Helpers #####

def _backspace(typed):
    print('\b \b', end='', flush=True)
    return typed[:len(typed)-1]

def _countdown(seconds):
    for i in range(int(seconds)):
        print(str(seconds-i) + '...', end='', flush=True)
        time.sleep(1)
    print('GO!!!')

##### Run the Trainer #####
'''    
_countdown(COUNTDOWN)
    
# Try to flush the buffer
while msvcrt.kbhit():
        msvcrt.getch()


revisited = {}
wrongWords = {}

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

        # Start the clock if it is the first character of the first word
        if(idx == 0 and typed == ''):totalTime = startTime = time.time()

        char = char.decode('utf-8')
        
        # Check to see if the word was typed wrong, disable typing if it is
        if(len(typed) > len(word)):
            currMistakes += 1
            continue

        # Print the character to the console
        print(char, end='', flush=True)
    
        if(word == typed and char == ' '):break

        typed += char
        
        # A mistake has been made
        if(word[:len(typed)] != typed):currMistakes += 1
        # Typing is finished
        elif(word == typed and idx == (len(paragraph)-1)):break
    
    if((currMistakes == 0) and (word not in generator.revisited)):continue
    
    wpm = (len(word) / AVERAGE_LENGTH) / ((time.time() - startTime) / 60)
    
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

print('\nFinished', end='\n\n')

##### Display the Result #####

totalWPM = int(len(paragraphString) / AVERAGE_LENGTH) / ((time.time() - totalTime) / 60)
print('Total WPM:', totalWPM, end='\n\n')

print('Revisted Words:')
for word in generator.revisited:
    print('"' + word + '":', revisited[word])

print('New mistakes:')
for word in wrongWords:
    print('"' + word + '":', wrongWords[word])

##### Save the Stats #####

def saveStats(stats, history, path):
    print('Saving stats...')
    history['recent'].append(totalWPM)
    if(len(history['recent']) > 10):history['recent'].pop(0)
    print('\nRecent WPM (10 Games):', np.average(history['recent']), end='\n\n')
    
    newLifetime = (stats['games'] * history['lifetime'] + totalWPM) / (stats['games'] + 1)
    stats['games'] += 1
    history['lifetime'] = newLifetime
    print('Lifetime WPM:', newLifetime, end='\n\n')
    
    # What kind of information needs to be saved?
    # 1. The word where the error occurred
    # 2. The severity(?) of the mistake:
        # - Time taken (wpm)
        # - Number of keystroke deviations
    with open(path, 'w') as f:
        json.dump(stats, f)
'''

def saveStats(stats, directory, userName):
    path = directory + userName + '.json'
    
    with open(path, 'w') as f:
        json.dump(stats, f)








