from ntpath import join
from pickle import TRUE
import sys
import numpy as np


#config
input_path = "../../res/data.text"
MAX_NODE = 100 #max number of nodes in the graph include points 0
MAX_CAR = 10
MAX_P_CAR = 1 #max people a car can carry

#Global variables
N=0
M=0
K=0
num_results = 0

visited = np.zeros(MAX_NODE, dtype='bool')
visited_k = np.zeros( (MAX_CAR, MAX_NODE), dtype='bool')

SIGMA = 0 # sum of M and N

p = np.zeros(MAX_NODE, dtype='int') #number of people in node i
q = np.zeros(MAX_NODE, dtype='int') #weight of goods in node i
Q = np.zeros(MAX_CAR, dtype='int') #max Capacity of car k
d = np.zeros((MAX_NODE, MAX_NODE), dtype='int') # d[i][j] travel distance bettwen node i and j

q_car = np.zeros(MAX_CAR, dtype='int') # capacity of car k in present
p_car = np.zeros(MAX_CAR, dtype='int') # number of people the car carry

q_car_res = np.zeros(MAX_CAR, dtype='int') # capacity of car k in present
p_car_res = np.zeros(MAX_CAR, dtype='int') # number of people the car carry

Y = np.zeros(MAX_CAR, dtype='int') # Y[k] is the first node of car k in the result graph
X = np.zeros(MAX_NODE, dtype='int') #X[v] is next node of v in the result graph

Y_res = np.zeros(MAX_CAR, dtype='int') # Y[k] is the first node of car k in the result graph
X_res = np.zeros(MAX_NODE, dtype='int') #X[v] is next node of v in the result graph

edges = 0 # The algorithm will end if edges = 2*Sigma + K
s = np.zeros(MAX_CAR, dtype='int') #sum travel distance of car k
res = sys.maxsize


def check_solution():
    global X, Y
    for i in range (1, K+1):
        v = Y[i]
        path = []
        # if (p_car[i] !=0 or q_car[i] !=0): return False
        while (v):
            path.append(v)
            if (v > SIGMA and (v-SIGMA not in path)): return False
            v = X[v]
    return True

def solution():
    global res, s, num_results, X_res, Y_res, X, Y, q_car_res, p_car_res, q_car, p_car
    num_results = num_results + 1

    # print("Travel distance (" + str(num_results) +") :" + str(s))
    # print("Path: ")
    # for i in range(1, K+1):
    #     path = ['0']
    #     v = Y[i]
    #     while (v):
    #         path.append(str(v))
    #         v = X[v]
    #     path.append('0')
    #     print("Car" + str(i) + " : " + '-'.join(tuple(path)))
    if (check_solution()):
        max_s = np.max(s[np.nonzero(s)])
        if max_s < res:
            X_res = np.copy(X)
            Y_res = np.copy(Y)
            p_car_res = np.copy(p_car)
            q_car_res = np.copy(q_car)
            res = max_s

def checkX(u,v,k):
    if (visited[u] and u !=0): return False
    if (u > SIGMA and visited_k[k][u-SIGMA] == False): return False
    if (u == 0 and k == K and edges != 2*SIGMA + K - 1): return False
    if (q_car[k] + q[u] > Q[k]): return False
    if (p_car[k] + p[u] > MAX_P_CAR): return False
    return True

def checkY(v,k):
    if (visited[v]): return False
    if (q_car[k] + q[v] > Q[k]): return False
    if (p_car[k] + p[v] > MAX_P_CAR): return False
    return True

def TryX(v,k):
    global s, edges
    for u in range(0, 2*SIGMA+1):
        if (checkX(u,v,k)) :
            X[v] = u
            visited[u] = True
            visited_k[k][u] = True
            p_car[k] = p_car[k] + p[u]
            q_car[k] = q_car[k] + q[u]
            s[k] = s[k] + d[v][u]
            edges = edges + 1

            if (u == 0):
                if (k == K):
                    if (edges == 2*SIGMA + K):
                        solution()
                else:
                    TryX(Y[k+1], k+1)
            else:
                TryX(u,k)

            edges = edges - 1
            s[k] = s[k] - d[v][u]
            q_car[k] = q_car[k] - q[u]
            p_car[k] = p_car[k] - p[u]
            visited_k[k][u] = False
            visited[u] = False


def TryY(k):
    global s, edges
    for v in range(1, SIGMA+1):
        if (checkY(v,k)) :
            Y[k] = v
            visited[v] = True
            visited_k[k][v] = True
            p_car[k] = p_car[k] + p[v]
            q_car[k] = q_car[k] + q[v]
            s[k] = s[k] + d[0][v]
            edges = edges + 1

            if (k==K) :
                TryX(Y[1], 1)
            else :
                TryY(k+1)

            edges = edges - 1
            s[k] = s[k]- d[0][v]
            q_car[k] = q_car[k] - q[v]
            p_car[k] = p_car[k] - p[v]
            visited_k[k][v] = False
            visited[v] = False
    return

def getInput() :
    global N, M, SIGMA, K, q, Q, d

    with open (input_path, "r") as f:

        lines = f.readlines()
        line = list(map(int,lines[0].strip().split()))
        N = line[0]
        M = line[1]
        SIGMA = N + M
        K = line[2]

        line = list(map(int,lines[1].strip().split()))
        for m in range(1,2*SIGMA +1):
            if (m<=N):
                p[m] = 1
            elif (m> SIGMA and m <= SIGMA + N):
                p[m] = -1
            if (m > N and m <= SIGMA):
                q[m] = line[m-N-1]
            elif (m>SIGMA+N and m <=2*SIGMA):
                q[m] = line[m-SIGMA-N-1]*(-1)
            else :
                q[m] = 0

        line = list(map(int,lines[2].strip().split()))
        for k in range(1,K+1):
            Q[k] = line[k-1]

        for i in range (0, 2*SIGMA+1):
            line = list(map(int,lines[i+3].strip().split()))
            for j in range(0, 2*SIGMA+1):
                d[i][j] = line[j]
    return

def main():
    getInput()
    for i in range(0, 2*SIGMA+1):
        visited[i] = False
    TryY(1)
    # print("Max travel distance: " + str(res))
    print("Path: ")
    for i in range(1, K+1):
        path = ['0']
        v = Y_res[i]
        while (v):
            path.append(str(v))
            v = X_res[v]
        path.append('0')
        print("Car" + str(i) + " : " + '-'.join(tuple(path)))
    print(f"Max distance: {res}" )

if __name__ == "__main__":
    main()