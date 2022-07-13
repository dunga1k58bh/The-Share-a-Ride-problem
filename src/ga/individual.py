
import numpy as np

class Individual():

    def __init__(self, ind, factorial_cost):
        self.__ind = ind
        self.__factorial_cost = factorial_cost
        self.__factorial_rank = []
        self.__taskMinRank = -1
        self.__skill_factor = -1
        pass


    def getInd(self):
        return self.__ind


    def getFactorialCost(self):
        return self.__factorial_cost


    def setFactorialRank(self, factorial_rank):
        self.__factorial_rank = factorial_rank

    def getFactorialRank(self):
        return self.__factorial_rank


    def taskMinRank(self):
        return self.__taskMinRank


    def setScalerFitness(self):
        self.__scaler_fitness = 1.0/min(self.__factorial_rank)


    def getScalerFitness(self):
        return self.__scaler_fitness


    def setSkillFactor(self, skill_factor):
        self.__skill_factor = skill_factor

    def getSkillFactor(self):
        return self.__skill_factor


