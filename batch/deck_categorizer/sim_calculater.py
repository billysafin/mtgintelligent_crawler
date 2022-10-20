#-*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

class CoOccurrence(metaclass = ABCMeta):
 
    @abstractmethod
    def calculate(self, token_list_x, token_list_y):
        raise NotImplementedError("This method must be implemented.")
 
    def unique(self, token_list_x, token_list_y):
        x = set(list(token_list_x))
        y = set(list(token_list_y))
        return x, y
 
    def count(self, token_list):
        token_dict = {}
        for token in token_list:
            if token in token_dict:
                token_dict[token]  = 1
            else:
                token_dict[token] = 1
        return token_dict
 
class Jaccard(CoOccurrence):
 
    def calculate(self, token_list_x, token_list_y):
        x, y = self.unique(token_list_x, token_list_y)
        try:
            result = len(x & y) / len(x | y)
        except ZeroDivisionError:
            result = 0.0
        return result
 
class Dice(CoOccurrence):
 
    def calculate(self, token_list_x, token_list_y):
        x, y = self.unique(token_list_x, token_list_y)
        try:
            result = 2 * len(x & y) / float(sum(map(len, (x, y))))
        except ZeroDivisionError:
            result = 0.0
        return result
    
class Simpson(CoOccurrence):
 
    def calculate(self, token_list_x, token_list_y):
        x, y = self.unique(token_list_x, token_list_y)
        try:
            result = len(x & y) / float(min(map(len, (x, y))))
        except ZeroDivisionError:
            result = 0.0
        return result

def jaccard_calculate(sample, to_compare):
    jaccard = Jaccard()
    result = jaccard.calculate(
        sample,
        to_compare
    )
    return result

def dice_calculate(sample, to_compare):
    dice = Dice()
    result = dice.calculate(
        sample,
        to_compare
    )
    return result

def simpson_calculate(sample, to_compare):
    simpson = Simpson()
    result = simpson.calculate(
        sample,
        to_compare
    )
    return result