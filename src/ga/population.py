from random import random
import numpy as np

from ga.individual import Individual

class Population():
    def __init__(self, pop_size, dimention):
        self.pop_size = pop_size
        self.ranks = []
        self._dimention = dimention

    def generate(self):
        self.__individuals = []

        for i in range(self.pop_size):
            ind = []
            for j in range(self._dimention):
                ind.append(np.random())

            if (self.checkInd(ind) == False):
                print("Generate population fail!")
                exit()
            c = []
            for j in range(self.__n_tasks):
                c.append(self.__tasks[j].evaluate(ind))

            individual = Individual(ind, c)
            self.__individuals.append(individual)

        self.updateRank()
        for ind in self.__individuals:
            ind.setSkillFactor(ind.getFactorialRank().index(min(ind.getFactorialRank())))
        return

    def checkInd(self, ind):
        
        return True

    def updateRank(self):
        ranks = []

        for i in range(self.__n_tasks):
            ranks.append([])

        for ind in self.__individuals:
            for j in range(self.__n_tasks):
                rank_j = ranks[j]
                check = True
                for k in range(len(rank_j)):
                    if (rank_j[k].getFactorialCost()[j] > ind.getFactorialCost()[j]):
                        rank_j.insert(k, ind)
                        check = False
                        break
                if check:
                    rank_j.append(ind)

        for ind in self.__individuals:
            factorial_rank = []
            min_rank = self.pop_size +2
            task_min_rank = -1

            for j in range (self.__n_tasks):
                rank_j_ind = ranks[j].index(ind) + 1
                factorial_rank.append(rank_j_ind)

                if (rank_j_ind < min_rank):
                    min_rank = rank_j_ind

            ind.setFactorialRank(factorial_rank)
            ind.setScalerFitness()

        return


    def updatePopulation(self):
        individuals = self.__individuals
        individuals.sort(key=lambda x: x.getScalerFitness(), reverse=True)
        individuals = individuals[:self.pop_size]
        self.__individuals = individuals

    def dimention(self):
        return self.__dimention

    def individuals(self):
        return self.__individuals

