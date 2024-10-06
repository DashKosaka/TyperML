# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 22:01:52 2018

@author: Dash
"""
import os, string, torch, random, json
from game.utils import plot_comparison, avg_time, med_time
from game.functions import rnn_output
from rnn.models import TimeRNN, ConfidenceRNN
from rnn.losses import single_conf_loss, single_time_loss
from rnn.utils import char_tensor

username = input('Username: ')
all_characters = string.printable
n_characters = len(all_characters)

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") 
user_saves = './users/'

# Parameter settings
hidden_size = 200
n_layers = 2
params = {'input_size':n_characters, 'hidden_size':hidden_size, 'n_layers':n_layers}

# Initialize the models
trnn = TimeRNN(**params).to(device)
crnn = ConfidenceRNN(**params).to(device)

# Load in weights
user_path = user_saves + username + '/'
trnn.load_state_dict(torch.load(user_path + 'time.pth'))
crnn.load_state_dict(torch.load(user_path + 'confidence.pth'))

# Get data paths
data_path = user_path + '/data/'
sequences_path = data_path + 'sequences.txt'
times_path = data_path + 'times_target.txt'
confs_path = data_path + 'confs_target.txt'

# Loading function
def load_data(path):
    return list(map(lambda x: x.strip('\n'), open(path).readlines()))

# Load in data
sequences = load_data(sequences_path)
times = list(map(lambda x: list(map(float, x.split())), load_data(times_path)))
confs = list(map(lambda x: list(map(lambda y: float(y)-.5, x.split())), load_data(confs_path)))

def process_times(times, prime=None):
    keys = []
    for seq in times:
        if prime is None:
            prime = seq[len(seq)-1]
        keys.append(prime)
        for i in range(len(seq)):
            seq[i] = (seq[i]/prime) - 1
    return keys

def center_times(times, prime):
    for seq in times:
        for i in range(len(seq)):
            seq[i] = seq[i] - prime
    
def undo_normalize(time, key):
    return (time + 1) * key

avg_t = avg_time(times)
med_t = med_time(times)
stats = {'avg_t':avg_t, 'med_t':med_t}
#time_keys = process_times(times, med_t)
center_times(times, med_t)

# Training parameters
EPOCHS = 30
learning_rate = 1e-4
#learning_rate = 5e-3

# Make the optimizers
t_solver = torch.optim.SGD(trnn.parameters(), lr=learning_rate)
t_criterion = single_time_loss
c_solver = torch.optim.SGD(crnn.parameters(), lr=learning_rate)
c_criterion = single_conf_loss

# Minibatch function
def minibatch(*arg):
    num_seq = len(arg[0])
    rand_idx = random.randint(0, num_seq-1)
    ret = []
    for file in arg:
        ret.append(file[rand_idx])
    return ret

# Training function
def train_on_sequence(rnn, sequence, target, optimizer, criterion, device=None):
    
    loss = 0
    hidden = rnn.init_hidden(1, device)
    for c, t in zip(sequence, target):
        c_tensor = char_tensor(c).to(device)
        pred, hidden = rnn(c_tensor, hidden)
        loss += criterion(pred, t, device)
    
    loss.backward()
    optimizer.step()
    return loss

# Training loop
for ep in range(EPOCHS):
    
    t_loss = 0
    c_loss = 0
    for char_seq, time_seq, conf_seq, idx in zip(sequences, times, confs, range(len(sequences))):
#    char_seq, time_seq, conf_seq = minibatch(sequences, times, confs)
#        with torch.no_grad():
#            t = rnn_output(trnn, char_seq, device)
        
        trnn.zero_grad()
        t_loss += train_on_sequence(trnn, char_seq, time_seq, t_solver, t_criterion, device)

#    print('Epoch:', ep)
#    print('Avg Time Loss: {}'.format(t_loss / len(sequences)))

        crnn.zero_grad()
        c_loss += train_on_sequence(crnn, char_seq, conf_seq, c_solver, c_criterion, device)

    t_loss /= len(sequences)    
    c_loss /= len(sequences)
    print('Epoch:', ep)
    print('Time Loss: {}\tConf Loss: {}'.format(t_loss, c_loss))

plot_comparison(rnn_output(trnn, char_seq, device), time_seq, med_t)
plot_comparison(rnn_output(crnn, char_seq, device), conf_seq)

print('Saving data')
# Save the weights
torch.save(trnn.state_dict(), user_path + 'time.pth')
torch.save(crnn.state_dict(), user_path + 'confidence.pth')

# Save the stats
with open(user_path + 'stats.json', 'w') as f:
    json.dump(stats, f)














