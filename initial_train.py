# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 23:23:21 2018

@author: Dash
"""
import os, string, random, torch
from rnn.models import TimeRNN, ConfidenceRNN, GenerateRNN
from rnn.losses import confidence_rnn_loss, time_rnn_loss
from rnn.utils import char_tensor

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") 
iters = 10000

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
crnn = ConfidenceRNN(**params).to(device)
grnn = GenerateRNN(**params, output_size=n_characters).to(device)

# Check if user exists
if username.lower() not in list(map(lambda x: x.lower(), os.listdir('./users'))):
    os.mkdir(user_saves + username)
    torch.save(trnn.state_dict(), user_saves + username + '/time.pth')
    torch.save(crnn.state_dict(), user_saves + username + '/confidence.pth')    

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
            diff = time * lamb_t - conf * lamb_c
            
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

t_optimizer = torch.optim.Adam(trnn.parameters(), lr=learning_rate)
c_optimizer = torch.optim.Adam(crnn.parameters(), lr=learning_rate)
for _ in range(iters):

    sequence, times, confs = generate(grnn, trnn, crnn, prime=None, sample_size=1, \
                                  temperature=.8, predict_len=seq_len, device=device)

    mistake_seq = [torch.tensor([.9]) for _ in range(len(sequence))]
    time_seq = [torch.tensor([.5]) for _ in range(len(sequence))]

    t_loss = time_rnn_loss(times, time_seq, device=device)
    t_loss.backward()
    t_optimizer.step()

    c_loss = confidence_rnn_loss(confs, mistake_seq, device=device)
    c_loss.backward()
    c_optimizer.step()
    
    print('Time loss: %f, Conf loss: %f' % (t_loss, c_loss))
    print(times[0], confs[0])

torch.save(trnn.state_dict(), user_path + 'time.pth')
torch.save(crnn.state_dict(), user_path + 'confidence.pth')
