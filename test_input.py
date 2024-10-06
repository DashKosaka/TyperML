# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 17:30:37 2018

@author: Dash
"""
import msvcrt

sequence = 'hello'
print(sequence)

def _backspace():
    print('\b \b', end='', flush=True)

user_word = ''
idx = 0
while idx < len(sequence):
    char = sequence[idx]
#for idx, char in enumerate(sequence):
    
    next_char = False
    curr_str = ''
    
    while not next_char:
        # Get keypress
        printFlag = True
        
        user_char = None
        while user_char is None:
            if msvcrt.kbhit():
                char_bin = msvcrt.getch()
                print(char_bin)
                user_char = char_bin.decode('utf-8')

        # Check if we can print the character
        if char_bin is b'\x08':
            _backspace()
            if curr_str is '':
                idx -= 2
                break
            curr_str = curr_str[:-1]
        else:
            curr_str += user_char
            print(user_char, end='', flush=True)
        
        if curr_str is char:
            user_word += curr_str
            next_char = True
            
    idx += 1
    if idx < 0:
        idx = 0
    
    


