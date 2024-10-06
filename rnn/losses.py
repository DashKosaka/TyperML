import torch
from torch.nn.functional import binary_cross_entropy as bce_loss
from torch.nn.functional import cross_entropy
from torch.nn.functional import mse_loss, l1_loss
from torch.nn import CrossEntropyLoss

def confidence_rnn_loss(pred_conf, target_conf, device=None):
	'''
	Compute the confidence rnn loss

	Inputs:
	- pred_conf: Output correctness confidence from ConfidenceRNN
	- target_conf: User's actual correctness performance
	'''
	loss = 0
	for p, t in zip(pred_conf, target_conf):
		loss += cross_entropy(p, t.to(device))
		# loss += bce_loss(p.view(1), t.view(1).to(device))
	# loss /= len(pred_conf)
	return loss

def time_rnn_loss(pred_time, target_time, device=None):
	'''
	Compute the time rnn loss

	Inputs:
	- pred_time: Output time from TimeRNN
	- target_time: User's actual time performance
	'''
	loss = 0
	for p, t in zip(pred_time, target_time):
		loss += mse_loss(p.squeeze(0), t.to(device))
	# loss /= len(pred_time)
	return loss

def single_conf_loss(pred_conf, target_conf, device=None):
	'''
	Compute the confidence rnn loss

	Inputs:
	- pred_conf: Output correctness confidence from ConfidenceRNN
	- target_conf: User's actual correctness performance
	'''
	return mse_loss(pred_conf.squeeze(0), torch.Tensor([target_conf]).to(device))

def single_time_loss(pred_time, target_time, device=None):
	'''
	Compute the time rnn loss

	Inputs:
	- pred_time: Output time from TimeRNN
	- target_time: User's actual time performance
	'''
	return mse_loss(pred_time.squeeze(0), torch.Tensor([target_time]).to(device))

def generator_rnn_loss(pred_conf, pred_chars, target_chars, conf_scale=1.0, chars_scale=1.0):
	'''
	Compute the generator rnn loss

	Inputs:
	- pred_conf: Predicted confidence from ConfidenceRNN
	- pred_chars: Predicted chars from GeneratorsRNN
	- target_chars: Real chars from chunk
	- conf_scale: Discount factor for conf
	- chars_scale: Discount factor for chars
	'''
	conf_loss = bce_loss(pred_conf, torch.zeros_like(pred_conf))

	chars_loss = CrossEntropyLoss(pred_chars, target_chars)

	return (conf_scale * conf_loss) + (chars_scale * chars_loss)



