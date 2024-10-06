# -*- coding: utf-8 -*-
"""
Created on Thu Dec  6 22:26:52 2018

@author: Dash
"""
import os, string, random, msvcrt, time, torch, sys
import matplotlib.pyplot as plt
import numpy as np
from game.functions import simple_generate, main_loop
from rnn.models import TimeRNN, ConfidenceRNN, GenerateRNN
from rnn.losses import confidence_rnn_loss, time_rnn_loss
from rnn.utils import char_tensor

#username = input('Username: ').lower()
username = sys.argv[1]
sess_len = int(sys.argv[2])

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") 

all_characters = string.printable
n_characters = len(all_characters)

# Parameter settings
hidden_size = 200
n_layers = 2
params = {'input_size':n_characters, 'hidden_size':hidden_size, 'n_layers':n_layers}
text_weights = 'ml.pth'
user_saves = './users/'
seq_len = 50

# Initialize the models
grnn = GenerateRNN(**params, output_size=n_characters).to(device)

# Check if user exists
if username not in list(map(lambda x: x.lower(), os.listdir('./users'))):
    os.mkdir(user_saves + username)
if 'data' not in list(map(lambda x: x.lower(), os.listdir('./users' + '/' + username))):
    os.mkdir(user_saves + username + '/' + 'data')    

# Load in weights
user_path = user_saves + username + '/'
grnn.load_state_dict(torch.load('rnn/weights/' + text_weights))

for _ in range(sess_len):

    sequence_orig = simple_generate(grnn, temperature=.8 , predict_len=seq_len, device=device)
    sequence_orig = sequence_orig.replace('\n', ' ')
    sequence = sequence_orig.replace(' ', '_').replace('\t', '_')
    
    print('\n')
    print(sequence)
    
    sys.stdin.flush()
    sys.stdout.flush()
    time_seq, conf_seq, skipped = main_loop(sequence)
    
    if not skipped:
        with open(user_path + '/data/sequences.txt', 'a') as f:
            f.write(sequence_orig + '\n')
        with open(user_path + '/data/times_target.txt', 'a') as f:
            f.write(' '.join(list(map(lambda x: str(float(x[0])), time_seq))) + '\n')
        with open(user_path + '/data/confs_target.txt', 'a') as f:
            f.write(' '.join(list(map(lambda x: str(int(x[0])), conf_seq))) + '\n')

print('\ndone')





