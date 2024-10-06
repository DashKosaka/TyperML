# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 00:15:42 2018

@author: Dash
"""
import os, string, random, msvcrt, time, torch
import matplotlib.pyplot as plt
import numpy as np
from rnn.models import TimeRNN, ConfidenceRNN, GenerateRNN
from rnn.losses import confidence_rnn_loss, time_rnn_loss
from rnn.utils import char_tensor

username = input('Username: ')

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") 

all_characters = string.printable
n_characters = len(all_characters)

# Parameter settings
hidden_size = 200
n_layers = 2
params = {'input_size':n_characters, 'hidden_size':hidden_size, 'n_layers':n_layers}
text_weights = 'shakespeare.pth'
user_saves = './users/'
seq_len = 50
learning_rate = 1.0

# Initialize the models
trnn = TimeRNN(**params).to(device)
crnn = ConfidenceRNN(**params, output_size=2).to(device)
grnn = GenerateRNN(**params, output_size=n_characters).to(device)

# Check if user exists
if username.lower() not in list(map(lambda x: x.lower(), os.listdir('./users'))):
    os.mkdir(user_saves + username)
    torch.save(trnn.state_dict(), user_saves + username + '/time.pth')
    torch.save(crnn.state_dict(), user_saves + username + '/confidence.pth')   
    os.mkdir(user_saves + username + '/' + 'data')

# Load in weights
user_path = user_saves + username + '/'
trnn.load_state_dict(torch.load(user_path + 'time.pth'))
crnn.load_state_dict(torch.load(user_path + 'confidence.pth'))
grnn.load_state_dict(torch.load('rnn/weights/' + text_weights))

# Generate a new sequence
def generate(G, T, C, lamb_t=.5, lamb_c=.5, prime=None, sample_size=3, predict_len=100, temperature=0.8, look_ahead=1, device=None):
    # Zero the gradients
    G.zero_grad()
    T.zero_grad()
    C.zero_grad()

    # Initialize hidden states
    g_hidden = G.init_hidden(1, device=device)
    t_hidden = T.init_hidden(1, device=device)
    c_hidden = C.init_hidden(1, device=device)

    # Start a random sequence
    if prime is None:
        sequence = random.choice(string.ascii_uppercase)
    else:
        sequence = prime
    prime_input = char_tensor(sequence).unsqueeze(0).to(device)
    
    # Use priming string to "build up" hidden state
    for p in range(len(prime_input) - 1):
        _, g_hidden = G(prime_input[:,p], g_hidden)
        time, t_hidden = T(prime_input[:,p], t_hidden)
        conf, c_hidden = C(prime_input[:,p], c_hidden)
    inp = prime_input[:,-1]
    
    times = []
    confs = []
    
    for p in range(predict_len):
        output, g_hidden = G(inp, g_hidden)
        
        # Sample from the network as a multinomial distribution
        output_dist = output.data.view(-1).div(temperature).exp()
        char_sample = torch.multinomial(output_dist, sample_size)

        # Set initals
        inp = None
        max_diff = float('-inf')
        worst_time = 0
        worst_conf = 1

        # First save the initial hidden states
        t_hidden_prev = t_hidden.clone()
        c_hidden_prev = c_hidden.clone()
        
        # Sample a character for the user to type
        for char_t in char_sample:
            char_t = char_t.unsqueeze(0)
            
            # Pass through both the judging RNNs
            time, _ = T(char_t, t_hidden)
            conf, _ = C(char_t, c_hidden)
            
            # Calculate the diff factor
            diff = time.squeeze(0)[0]* lamb_t - conf.squeeze(0)[0] * lamb_c
            
            # Check if new best
            if diff > max_diff:
                worst_time = time
                worst_conf = conf
                inp = char_t
                max_diff = diff
                
            # Reset hiddens
            t_hidden = t_hidden_prev.clone()
            c_hidden = c_hidden_prev.clone()
        
        # Set the next character to the best results
        time, t_hidden = T(inp, t_hidden)
        conf, c_hidden = C(inp, c_hidden)
        sequence += all_characters[inp[0]]
    
        times.append(worst_time)
        confs.append(worst_conf)
    
            
    return sequence[1:], times, confs

print()
sequence, times, confs = generate(grnn, trnn, crnn, prime='T', sample_size=1, \
                                  temperature=.2 , predict_len=seq_len, device=device)
sequence = sequence.replace('\n', ' ').replace(' ', '_')
print(sequence)

# Let user try and type the sequence
user_word = ''
conf_seq = [torch.ones(1, dtype=torch.long) for _ in range(len(sequence))]
time_seq = [torch.zeros(1) for _ in range(len(sequence))]

def _backspace():
    print('\b \b', end='', flush=True)

user_word = ''
idx = 0
while idx < len(sequence):
    # Get the current char in the sequence
    char = sequence[idx]
                    
    # Get the loop ready
    next_char = False
    curr_str = ''
    init_time = time.time()
    while not next_char:
        
        # Capture the user input
        user_char = None
        while user_char is None:
            if msvcrt.kbhit():
                char_bin = msvcrt.getch()
                user_char = char_bin.decode('utf-8')

        # Check if we can print the character
        if char_bin is b'\x08':
            _backspace()
            if curr_str is '':
                idx -= 2
                break
            curr_str = curr_str[:-1]
        elif char_bin is b'\r':
            print()
            curr_str += user_char
        else:
            curr_str += user_char
            print(user_char, end='', flush=True)
        
        # Check if the user can move on
        if curr_str is char or (char is '_' and curr_str is ' '):
            user_word += curr_str
            next_char = True
            time_seq[idx] += time.time()-init_time
        else:            
            conf_seq[np.clip(idx, 0, len(sequence)-1)] = torch.zeros(1, dtype=torch.long)
            
    # Go to next char
    idx += 1
    if idx < 0:
        idx = 0

with open(user_path + '/data/sequences.txt', 'a') as f:
    f.write(sequence + '\n')
with open(user_path + '/data/times_target.txt', 'a') as f:
    f.write(' '.join(list(map(lambda x: str(float(x[0])), time_seq))) + '\n')
with open(user_path + '/data/confs_target.txt', 'a') as f:
    f.write(' '.join(list(map(lambda x: str(int(x[0])), conf_seq))) + '\n')
    
# Save the data
torch.save(trnn.state_dict(), user_path + 'time.pth')
torch.save(crnn.state_dict(), user_path + 'confidence.pth')
    
    
    















