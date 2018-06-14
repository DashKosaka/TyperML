# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 03:12:33 2018

@author: Dash

Class of a Markov Chain used for sentence generation
"""
import numpy as np
import random
import sys

class MarkovChain:
    
    def __init__(self, file, stats):
        
        self.words = open(file).read().split()        
        
        self.cache = {}
        
        self._populateCache()
        
        self.paragraph = []
        
        self.stats = stats
    
    def _groupByThrees(self):
        
        if(len(self.words) < 3):
            sys.exit('There were not enough words in the given text file!')
        
        for i in range(2, len(self.words)):
            result = self.words[i]
            
            w1 = self.words[i-2]
            w2 = self.words[i-1]

            yield (w1, w2, result)
    
    def _populateCache(self):
        
        for w1, w2, result in self._groupByThrees():
            
            key = (w1, w2)
            
            if(key in self.cache.keys()):self.cache[key].append(result)
            else:self.cache[key] = [result]
                

    def newParagraph(self, size=100):
        
        keys = list(self.cache.keys())
        w1, w2 = random.choice(keys)
        
        self.paragraph = [w1, w2]
        
        while(len(self.paragraph) < size):
            key = (w1, w2)
            
            w1 = w2

            try:w2 = np.random.choice(self.cache[key])
            except:w1, w2 = random.choice(keys)

            self.paragraph.append(w2)   
        
        return self.paragraph

    def asString(self):
        
        return ' '.join(self.paragraph)

    def _epsilonGreedy(self):
        
        return True
    











