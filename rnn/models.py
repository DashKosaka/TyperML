import torch
import torch.nn as nn
import torch.nn.functional as F

class GenerateRNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, n_layers=1):
        '''
        Initalize a GenerateRNN object to produce characters

        Inputs: 
        - input_size: Size of the 1-hot encoded char tensor
        - hidden_size: Size of the internal weight size of the RNN
        - output_size: Size of the 1-hot encoded char tensor
        - n_layers: Number of forward layers until output in the RNN
        '''
        super(GenerateRNN, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.n_layers = n_layers

        self.embed = nn.Embedding(input_size, hidden_size)
        self.rnn = nn.GRU(input_size=hidden_size, hidden_size=hidden_size, num_layers=n_layers)
        self.output = nn.Linear(hidden_size, output_size)

    def forward(self, input, hidden):
        batch_size = input.size()[0]

        # First embed the input
        embedding = self.embed(input)
        embedding = embedding.view(-1, batch_size, self.hidden_size)

        # Pass through rnn
        output, hidden = self.rnn(embedding, hidden)

        # Get the char output
        output = self.output(output)        

        return output, hidden

    def init_hidden(self, batch_size, device=None):
        """
        Initialize hidden states to all 0s during training.

        Inputs:
        - batch_size: batch size

        Returns:
        - hidden: initialized hidden values for input to forward function
        """
        hidden = torch.zeros(self.n_layers, batch_size, self.hidden_size, requires_grad=False).to(device)

        return hidden

class ConfidenceRNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size=1, n_layers=1):
        '''
        Initalize a ConfidenceRNN object to predict correctness

        Inputs: 
        - input_size: Size of the 1-hot encoded char tensor
        - hidden_size: Size of the internal weight size of the RNN
        - n_layers: Number of forward layers until output in the RNN
        '''
        super(ConfidenceRNN, self).__init__()
        self.input_size = input_size
        self.output_size = output_size
        self.hidden_size = hidden_size
        self.n_layers = n_layers

        self.embed = nn.Embedding(input_size, hidden_size)
        self.rnn = nn.GRU(input_size=hidden_size, hidden_size=hidden_size, num_layers=n_layers)
        self.linear = nn.Linear(hidden_size, output_size)

    def forward(self, input, hidden):
        batch_size = input.size()[0]

        # First embed the input
        embedding = self.embed(input)
        embedding = embedding.view(-1, batch_size, self.hidden_size)

        # Pass through rnn
        output, hidden = self.rnn(embedding, hidden)

        # Get the confidence output
        output = output.view(-1, self.hidden_size)
        # output = self.sigmoid(self.linear(output))
        output = self.linear(output)

        return output, hidden

    def init_hidden(self, batch_size, device=None):
        """
        Initialize hidden states to all 0s during training.

        Inputs:
        - batch_size: batch size

        Returns:
        - hidden: initialized hidden values for input to forward function
        """
        hidden = torch.zeros(self.n_layers, batch_size, self.hidden_size, requires_grad=True).to(device)

        return hidden

class TimeRNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size=1, n_layers=1):
        '''
        Initalize a TimeRNN object to predict time taken

        Inputs: 
        - input_size: Size of the 1-hot encoded char tensor
        - hidden_size: Size of the internal weight size of the RNN
        - n_layers: Number of forward layers until output in the RNN
        '''
        super(TimeRNN, self).__init__()
        self.input_size = input_size
        self.output_size = output_size
        self.hidden_size = hidden_size
        self.n_layers = n_layers

        self.embed = nn.Embedding(input_size, hidden_size)
        self.rnn = nn.GRU(input_size=hidden_size, hidden_size=hidden_size, num_layers=n_layers)
        self.linear = nn.Linear(hidden_size, output_size)

    def forward(self, input, hidden):
        batch_size = input.size()[0]

        # First embed the input
        embedding = self.embed(input)
        embedding = embedding.view(-1, batch_size, self.hidden_size)

        # Pass through rnn
        output, hidden = self.rnn(embedding, hidden)

        # Get the confidence output
        output = output.view(-1, self.hidden_size)
        # output = F.relu(self.linear(output))
        output = self.linear(output)

        return output, hidden

    def init_hidden(self, batch_size, device=None):
        """
        Initialize hidden states to all 0s during training.

        Inputs:
        - batch_size: batch size

        Returns:
        - hidden: initialized hidden values for input to forward function
        """
        hidden = torch.zeros(self.n_layers, batch_size, self.hidden_size, requires_grad=True).to(device)

        return hidden
