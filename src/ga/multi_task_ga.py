import random

from ga.individual import Individual
from ga.population import Population


class MultiTaskGA() :


    def __init__(self, pop_size, p_crossover,p_mutation, time_reset):
        self.time_reset = time_reset
        self.p_crossover = p_crossover
        self.p_mutation = p_mutation
        self.population = Population(pop_size)

        self.population.generate()
        self.dimention = self.population.dimention()
        self.bestInd = []


    def run(self, num_gen):

        self.population.generate()

        self.bestInd = self.population.individuals()[i]


        for gen in range(num_gen):
            individuals = self.population.individuals()
            childs = []

            n_crossover = int(self.population.pop_size * self.p_crossover)
            n_mutation = int(self.population.pop_size * self.p_mutation)
            cross_inds = random.sample(individuals, n_crossover)

            # Cross over
            i = 0
            while i < n_crossover:
                s1 = self.crossover(cross_inds[i], cross_inds[i+1])
                s2 = self.crossover(cross_inds[i+1], cross_inds[i])
                if (s1):
                    childs.append(s1)
                if (s2):
                    childs.append(s2)
                i = i + 2

            # Mutation
            mutate_inds = random.sample(individuals, n_mutation)

            for ind in mutate_inds:
                child = self.mutation(ind)
                if (child):
                    childs.append(child)

            individuals.extend(childs)
            self.updateRank()
            self.updatePopulation()
            self.updateBestInd()


        for i in range(self.n_tasks):
            print(f"Task {i}\n Solution: ")
            print(self.tasks[i].decode(self.bestInd[i].getInd()))
            print(f"Fitness: {self.bestInd[i].getFactorialCost()[i]}")


    def crossover(self, individual1: Individual, individual2: Individual):
        ind1 = individual1.getInd()
        ind2 = individual2.getInd()
        child_ind = []
        p = random.randint(0, self.dimention)

        for i in range (p):
            child_ind.append(ind1[i])

        for i in range(p, self.dimention):
            child_ind.append(ind2[i])

        if (individual1.taskMinRank() < individual2.taskMinRank()):
            child_skill_factor = individual1.getSkillFactor()
        else :
            child_skill_factor = individual2.getSkillFactor()

        child_factorial_cost = []
        for i in range(self.n_tasks):
            if (i == child_skill_factor):
                child_factorial_cost.append(self.tasks[i].evaluate(child_ind))
            else:
                child_factorial_cost.append(999999)
            if (self.tasks[i].checkInd(child_ind) == False):
                return None


        child = Individual(child_ind, child_factorial_cost)
        child.setSkillFactor(child_skill_factor)
        
        return child


    def mutation(self, individual: Individual):
        ind = individual.getInd()
        child_ind = ind.copy()
        mutateCoefficient = int(self.dimention*0.1)
        count = random.randint(0, mutateCoefficient)
        for i in range(count):
            p1 = random.randint(0,self.dimention-1)
            p2 = random.randint(0,self.dimention-1)

            temp = child_ind[p1]
            child_ind[p1] = child_ind[p2]
            child_ind[p2] = temp

        child_skill_factor = individual.getSkillFactor()
        child_factorial_cost = []

        for i in range (self.n_tasks):
            if (i == child_skill_factor):
                child_factorial_cost.append(self.tasks[i].evaluate(child_ind))
            else:
                child_factorial_cost.append(999999)
            if (self.tasks[i].checkInd(child_ind) == False):
                return None

        child = Individual(child_ind, child_factorial_cost)
        child.setSkillFactor(child_skill_factor)
        return child


    def updatePopulation(self):
        self.population.updatePopulation()


    def updateRank(self):
        self.population.updateRank()


    def updateBestInd(self):
        for i in range(self.n_tasks):
            ind = self.population.individuals()[i]
            skill_factor = ind.getSkillFactor()
            if (ind.getFactorialCost()[skill_factor] < self.bestInd[skill_factor].getFactorialCost()[skill_factor]):
                self.bestInd[skill_factor] = ind

