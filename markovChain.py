# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 03:12:33 2018

@author: Dash

Class of a Markov Chain used for sentence generation
"""
import numpy as np
import random, sys, copy, os

class MarkovChain:
    
    def __init__(self, directory, stats, epsilon=.25):

        self.words = []        

        for (path, dirName, fileList) in os.walk(directory):
            for file in fileList:
                fileWords = open(path + '/' + file).read().split()
                self.words.extend(fileWords)
        
        self.cache = {}
        self._populateCache()
        
        self.paragraph = []
        
        self.wordStats = stats
        self.keys = list(self.wordStats.keys())
        self.distribution = self._makeDistribution()

        self.epsilon = epsilon
    
        
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
                
    def _makeDistribution(self):
        
        distribution = []
        
        for key in self.keys:
            
            stat = self.wordStats[key]
            
            distribution.append(stat['mistakes'] / stat['biased'])

        return self._normalize(distribution)

    def _normalize(self, distribution):
        total = sum(distribution)
        return [x / total for x in distribution]

    def newParagraph(self, size=100):
        
        keys = list(self.cache.keys())
        w1, w2 = random.choice(keys)
        
        past = copy.deepcopy(self.keys)
        distribution = copy.deepcopy(self.distribution)
        
        self.revisited = []
        self.paragraph = [w1, w2]
        
        while(len(self.paragraph) < size):
            key = (w1, w2)
            
            w1 = w2
            if(random.random() < self.epsilon and len(past) > 0):
                w2 = np.random.choice(past, p=distribution)
                idx = past.index(w2)
                past.pop(idx)
                distribution.pop(idx)
                distribution = self._normalize(distribution)
                self.revisited.append(w2)
            else:
                try:w2 = np.random.choice(self.cache[key])
                except:w1, w2 = random.choice(keys)

            self.paragraph.append(w2)   
        
        return self.paragraph

    def asString(self):
        
        return ' '.join(self.paragraph)










