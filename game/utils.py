# -*- coding: utf-8 -*-
"""
Created on Sat Dec  8 03:57:23 2018

@author: Dash
"""
import torch
import matplotlib.pyplot as plt

def process_tensor_list(tensor_list):
    ret = []
    for tensor in tensor_list:
        ret.append(tensor.squeeze(0))
    return ret
    
def plot_time(pred, target, key=None, pred_color='r', target_color='b'):
    pred_list = process_tensor_list(pred)
    target_copy = []
    if key:
        for idx in range(len(pred_list)):
            pred_list[idx] = (pred_list[idx] + 1) * key
            target_copy.append((target[idx]+1) * key)
        plt.plot(range(len(target_copy)), target_copy, c=target_color, label='target')
    else:
        plt.plot(range(len(target)), target, c=target_color, label='target')
    plt.plot(range(len(pred_list)), pred_list, c=pred_color, label='pred')
    plt.show()
    
def plot_confidence(pred, target, pred_color='r', target_color='b'):   
    pred_list = process_tensor_list(pred)
    target_copy = []
    key = .5
    for idx in range(len(pred_list)):
        pred_list[idx] = torch.round(pred_list[idx] + key)
        target_copy.append(target[idx] + key)
    plt.plot(range(len(target_copy)), target_copy, c=target_color, label='target')
    plt.plot(range(len(pred_list)), pred_list, c=pred_color, label='pred')
    plt.show()
    
def plot_comparison(pred, target, key=None, pred_color='r', target_color='b'):
    pred_list = process_tensor_list(pred)
    target_copy = []
    if key:
        for idx in range(len(pred_list)):
            pred_list[idx] = pred_list[idx] + key
            target_copy.append(target[idx] + key)
        plt.plot(range(len(target_copy)), target_copy, c=target_color, label='target')
    else:
        plt.plot(range(len(target)), target, c=target_color, label='target')           
    plt.plot(range(len(pred_list)), pred_list, c=pred_color, label='pred')
    plt.legend()
    plt.show()
    
def avg_time(times):
    avg_t = 0
    num_t = 0
    for seq in times:
        avg_t += sum(seq)
        num_t += len(seq)
    return avg_t / num_t

def med_time(times):
    med_list = []
    for seq in times:
        med_list.extend(seq)
    med_list.sort()
    return med_list[len(med_list)//2]
