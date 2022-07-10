from ortools.linear_solver import pywraplp
import numpy as np


def getInput(input_path):
    tmp = []
    with open(input_path, "r") as f:
        for i in f.readlines():
            i = i.replace("\n", "")
            i = i.rstrip(" ").split(" ")
            tmp.append([int(j) for j in i])
        f.close()
    return tmp

def main():
    # Input
    tmp = getInput('../res/data.text')
    distanceMatrix = tmp[3:]
    passengerNumber = tmp[0][0]
    parcelNumber = tmp[0][1]
    sumOfPassengerAndParcel = passengerNumber + parcelNumber
    taxiNumber = tmp[0][2]
    parcelWeight = tmp[1]
    maxWeightTaxi = tmp[2]

    solver = pywraplp.Solver.CreateSolver('SCIP')
    infinity = solver.infinity()

    # Variables
    x = []
    for i in range(2 * sumOfPassengerAndParcel + 1):
        x.append([])
        for j in range(2 * sumOfPassengerAndParcel + 1):
            x[i].append([])
            for k in range(taxiNumber):
                x[i][j].append(solver.IntVar(0, 1, 'x[{}][{}][{}]'.format(i, j, k)))
    y = []
    for i in range(sumOfPassengerAndParcel):
        y.append([])
        for k in range(taxiNumber):
            y[i].append(solver.IntVar(0, 1, 'y[{}][{}]'.format(i, k)))
    Z = solver.NumVar(0, infinity, 'Z')
    u = []
    for i in range(2 * sumOfPassengerAndParcel):
        u.append([])
        for k in range(taxiNumber):
            u[i].append(solver.IntVar(1, 2 * sumOfPassengerAndParcel, 'u[{}][{}]'.format(i, k)))
    r = []
    for i in range(2 * sumOfPassengerAndParcel + 1):
        r.append([])
        for k in range(taxiNumber):
            r[i].append(solver.IntVar(0, maxWeightTaxi[k], 'r[{}][{}]'.format(i, k)))
    v = []
    for i in range(2 * sumOfPassengerAndParcel + 1):
        v.append([])
        for k in range(taxiNumber):
            v[i].append(solver.IntVar(0, 1, 'v[{}][{}]'.format(i, k)))
    q = []
    for i in range(passengerNumber + 1):
        q.append(0)
    for i in range(passengerNumber + 1, sumOfPassengerAndParcel + 1):
        q.append(parcelWeight[i - passengerNumber - 1])
    for i in range(sumOfPassengerAndParcel + 1, 2 * passengerNumber + parcelNumber + 1):
        q.append(0)
    for i in range(2 * passengerNumber + parcelNumber + 1, 2 * sumOfPassengerAndParcel + 1):
        q.append(-parcelWeight[i - 2 * passengerNumber - parcelNumber - 1])
    t = []
    for i in range(passengerNumber + 1):
        t.append(1)
    for i in range(passengerNumber + 1, sumOfPassengerAndParcel + 1):
        t.append(0)
    for i in range(sumOfPassengerAndParcel + 1, 2 * passengerNumber + parcelNumber + 1):
        t.append(-1)
    for i in range(2 * passengerNumber + parcelNumber + 1, 2 * sumOfPassengerAndParcel + 1):
        t.append(0)
    print('Number of variables = ', solver.NumVariables())

    # Constrait
    #2.2
    for k in range(taxiNumber):
        solver.Add(sum(distanceMatrix[i][j] * x[i][j][k] for i in range(2 * sumOfPassengerAndParcel + 1) for j in range(2* sumOfPassengerAndParcel + 1)) <= Z)
    #2.3
    for k in range(taxiNumber):
        solver.Add(sum(x[0][i][k] for i in range(1, 2 * sumOfPassengerAndParcel + 1)) == 1)
    for k in range(taxiNumber):
        solver.Add(sum(x[i][0][k] for i in range(1, 2 * sumOfPassengerAndParcel + 1)) == 1)
    #2.4
    for i in range(1, sumOfPassengerAndParcel + 1):
        for k in range(taxiNumber):
            solver.Add(sum(x[i][j][k] for j in range(2 * sumOfPassengerAndParcel + 1)) - x[i][i][k] == y[i - 1][k])
    for i in range(1, sumOfPassengerAndParcel + 1):
        for k in range(taxiNumber):
            solver.Add(sum(x[j][i][k] for j in range(2 * sumOfPassengerAndParcel + 1)) - x[i][i][k] == y[i - 1][k])
    #2.5
    for i in range(sumOfPassengerAndParcel + 1, 2 * sumOfPassengerAndParcel + 1):
        for k in range(taxiNumber):
            solver.Add(sum(x[i][j][k] for j in range(2 * sumOfPassengerAndParcel)) - x[i][i][k] == y[i - sumOfPassengerAndParcel - 1][k])
    for i in range(sumOfPassengerAndParcel + 1, 2 * sumOfPassengerAndParcel + 1):
        for k in range(taxiNumber):
            solver.Add(sum(x[j][i][k] for j in range(2 * sumOfPassengerAndParcel)) - x[i][i][k] == y[i - sumOfPassengerAndParcel - 1][k])
    #2.6
    for i in range(1, 2 * sumOfPassengerAndParcel + 1):
        solver.Add(sum(x[i][j][k] for k in range(taxiNumber) for j in range(2 * sumOfPassengerAndParcel + 1)) - sum(x[i][i][k] for k in range(taxiNumber)) == 1)

    for i in range(1, 2 * sumOfPassengerAndParcel + 1):
        for j in range(1, 2 * sumOfPassengerAndParcel + 1):
            if j != i:
                for k in range(taxiNumber):
                    solver.Add(u[i - 1][k] - u[j - 1][k] + 2 * sumOfPassengerAndParcel * x[i][j][k] <= 2 * sumOfPassengerAndParcel - 1)

    for i in range(1, sumOfPassengerAndParcel + 1):
        for j in range(2 * sumOfPassengerAndParcel + 1):
            for k in range(taxiNumber):
                solver.Add(r[i][k] <= r[j][k] + q[i] * y[i - 1][k] + maxWeightTaxi[k] * (1 - x[j][i][k]))
    for i in range(sumOfPassengerAndParcel + 1, 2 * sumOfPassengerAndParcel + 1):
        for j in range(2 * sumOfPassengerAndParcel + 1):
            for k in range(taxiNumber):
                solver.Add(r[i][k] <= r[j][k] + q[i] * y[i - sumOfPassengerAndParcel - 1][k] + maxWeightTaxi[k] * (1 - x[j][i][k]))    

    for i in range(1, sumOfPassengerAndParcel + 1):
        for j in range(2 * sumOfPassengerAndParcel + 1):
            for k in range(taxiNumber):
                solver.Add(r[i][k] >= r[j][k] + q[i] * y[i - 1][k] + maxWeightTaxi[k] * (x[j][i][k] - 1))
    for i in range(sumOfPassengerAndParcel + 1, 2 * sumOfPassengerAndParcel + 1):
        for j in range(2 * sumOfPassengerAndParcel + 1):
            for k in range(taxiNumber):
                solver.Add(r[i][k] >= r[j][k] + q[i] * y[i - sumOfPassengerAndParcel - 1][k] + maxWeightTaxi[k] * (x[j][i][k] - 1)) 

    for i in range(1, 2 * sumOfPassengerAndParcel + 1):
        for k in range(taxiNumber):
            solver.Add(r[i][k] >= 0)
    for i in range(2 * sumOfPassengerAndParcel + 1):
        for k in range(taxiNumber):
            solver.Add(r[i][k] <= maxWeightTaxi[k])

    for k in range(taxiNumber):
        solver.Add(r[0][k] == 0)

    for i in range(1, sumOfPassengerAndParcel + 1):
        for j in range(2 * sumOfPassengerAndParcel + 1):
            for k in range(taxiNumber):
                solver.Add(v[i][k] <= v[j][k] + t[i] * y[i - 1][k] + maxWeightTaxi[k] * (1 - x[j][i][k]))
    for i in range(sumOfPassengerAndParcel + 1, 2 * sumOfPassengerAndParcel + 1):
        for j in range(2 * sumOfPassengerAndParcel + 1):
            for k in range(taxiNumber):
                solver.Add(v[i][k] <= v[j][k] + t[i] * y[i - sumOfPassengerAndParcel - 1][k] + maxWeightTaxi[k] * (1 - x[j][i][k]))

    for i in range(1, sumOfPassengerAndParcel + 1):
        for j in range(2 * sumOfPassengerAndParcel + 1):
            for k in range(taxiNumber):
                solver.Add(v[i][k] >= v[j][k] + t[i] * y[i - 1][k] + maxWeightTaxi[k] * (x[j][i][k] - 1))
    for i in range(sumOfPassengerAndParcel + 1, 2 * sumOfPassengerAndParcel + 1):
        for j in range(2 * sumOfPassengerAndParcel + 1):
            for k in range(taxiNumber):
                solver.Add(v[i][k] >= v[j][k] + t[i] * y[i - sumOfPassengerAndParcel - 1][k] + maxWeightTaxi[k] * (x[j][i][k] - 1))

    for k in range(taxiNumber):
        solver.Add(v[0][k] == 0)

    for i in range(2 * sumOfPassengerAndParcel + 1):
        for k in range(taxiNumber):
            solver.Add(x[i][i][k] == 0)
    print("Number of constraints = ", solver.NumConstraints())

    solver.Minimize(Z)
    status = solver.Solve()
    if status == pywraplp.Solver.FEASIBLE or status == pywraplp.Solver.OPTIMAL:
        print("Solution: ")
        print("Objective value = ", solver.Objective().Value())
        for k in range(taxiNumber):
          print("-- Vehicle {} --".format(k))
          l = []
          start = 0
          while True:
            l.append(start)
            print("Point {}, capacity: {}, number of passenger: {}".format(start, r[start][k].solution_value(), v[start][k].solution_value()))
            for i in range(2 * sumOfPassengerAndParcel + 1):
              if x[start][i][k].solution_value() == 1:
                start = i
                break
            if i == 0:
              break
          print("++ Visiting order: {} ++".format(l))
          s = distanceMatrix[l[-1]][0]
          for i in range(1, len(l)):
            s += distanceMatrix[l[i-1]][l[i]]
          print("++ Distance: {} ++".format(s))
    else:
        print('The problem does not have an optimal solution.')


if __name__ == "__main__":
    main()
