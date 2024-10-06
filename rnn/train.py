from losses import *

def sequence(G, C):
    '''
    Generate a new sequence of chars

    Inputs:
    - G: Generator RNN
    - C: Confidence RNN
    '''

    return

def update(G, C, input, target, optimizer, device=None):
    '''
    Update the weights of the Generator and Confidence RNNs

    Inputs:
    - G: Generator RNN
    - C: Confidence RNN
    - input: Input character data tensor
    - target: Target character data tensor
    - optimizer: Model optimizer
    - device: Computation device
    '''
    # Init hidden states
    G_hidden = None
    C_hidden = None
    pred_char = []
    pred_conf = []

    # Zero out grads
    G.zero_grad()
    C.zero_grad()

    # Iterate through the input
    for idx in range(len(input)):
        char, G_hidden = G.forward(input[idx], G_hidden)

        pred_char.append(char)

        pred_conf.append()


    pred_char = torch.tensor(pred_char).view(len(input), -1)
    pred_conf = torch.tensor(pred_conf).view(-1, 1)

    C_loss = confidence_rnn_loss(pred_conf)
    G_loss = generator_rnn_loss()

    return losses
