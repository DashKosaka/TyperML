# -*- coding: utf-8 -*-
"""
Created on Thu Dec  6 23:09:05 2018

@author: Dash
"""
import string, random, msvcrt, time, torch, sys
import numpy as np
all_characters = string.printable
write = sys.stdout.write

# Deal with backspace while typing
def _backspace():
    write('\b \b')
    sys.stdout.flush()
#    write(' ')
#    sys.stdout.flush()
#    write('\b')
#    sys.stdout.flush()

def putc(c):
    write(c)
    sys.stdout.flush()

# Turning a string into a tensor
def char_tensor(string):
    tensor = torch.zeros(len(string), requires_grad=True).long()
    for c in range(len(string)):
        try:
            tensor[c] = all_characters.index(string[c])
        except:
            continue
    return tensor

# Generate a new sequence w/ times & confs
def generate(G, T, C, lamb_t=.5, lamb_c=.5, prime=None, sample_size=3, rand_gen=False, predict_len=100, temperature=0.8, look_ahead=1, device=None):
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
        if rand_gen:
            output_dist = output.data.view(-1).div(temperature).exp()
            char_sample = torch.multinomial(output_dist, sample_size)
        else:
            char_sample = torch.topk(output.data.view(-1), sample_size)[1]

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
            
            print('Time:{}, Conf:{}'.format(time.data[0], conf.data[0]))
            
            # Calculate the diff factor
            diff = (time.squeeze(0)[0]* lamb_t) + ((1 - conf.squeeze(0)[0]) * lamb_c)
            
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

# Generate a new sequence
def simple_generate(G, prime=None, predict_len=100, temperature=0.8, look_ahead=1, device=None):
    # Initialize hidden states
    g_hidden = G.init_hidden(1, device=device)

    # Start a random sequence
    if prime is None:
        sequence = random.choice(string.ascii_uppercase)
    else:
        sequence = prime
    prime_input = char_tensor(sequence).unsqueeze(0).to(device)
    
    # Use priming string to "build up" hidden state
    for p in range(len(prime_input) - 1):
        _, g_hidden = G(prime_input[:,p], g_hidden)
    inp = prime_input[:,-1]
    
    for _ in range(predict_len):
        output, g_hidden = G(inp, g_hidden)
        
        # Sample from the network as a multinomial distribution
        output_dist = output.data.view(-1).div(temperature).exp()
        inp = torch.multinomial(output_dist, 1)[0]
        
        char = all_characters[inp]
        sequence += char
        inp = char_tensor(char).unsqueeze(0).to(device)
            
    return sequence[1:]

# Sample rnn
def rnn_output(rnn, sequence, device):
    hidden = rnn.init_hidden(1, device)
    
    output = []
    for char in sequence:
        c_tensor = char_tensor(char).to(device)
        
        pred, hidden = rnn(c_tensor, hidden)
        output.append(pred)
    
    return output

# Games main loop
def main_loop(sequence):
    # Let user try and type the sequence
    conf_seq = [torch.ones(1, dtype=torch.long) for _ in range(len(sequence))]
    time_seq = [torch.zeros(1) for _ in range(len(sequence))]
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
            if char_bin is b'\x08' or user_char is '\b':
                _backspace()
                if curr_str is '':
                    idx -= 2
                    break
                curr_str = curr_str[:-1]
                
            # Skip the current
            elif char_bin is b'\r':
                print('\nSkipping...')
                return time_seq, conf_seq, True
            
            # Regular character
            else:
                curr_str += user_char
                if user_char is ' ':
                    putc('_')
                else:
                    putc(user_char)
            
            # Check if the user can move on
            if curr_str is char or (char is '_' and curr_str is ' '):
                time_seq[idx] += time.time()-init_time
                next_char = True
            else:            
                conf_seq[np.clip(idx+len(curr_str), 0, len(sequence)-1)] = torch.zeros(1, dtype=torch.long)
                
        # Go to next char
        idx += 1
        if idx < 0:
            idx = 0
    
    return time_seq, conf_seq, False