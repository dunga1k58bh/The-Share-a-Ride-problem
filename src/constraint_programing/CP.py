from ortools.sat.python import cp_model
import numpy as np




def create_data_model(path):
    #Store the data model of the problem
    data = {}
    with open (path, "r") as f:
        lines = f.readlines()
        line = list(map(int,lines[0].strip().split()))
        N = line[0]
        M = line[1]
        SIGMA = N + M
        K = line[2]
        p = np.zeros(2*SIGMA +1, dtype='int')
        q = np.zeros(2*SIGMA +1, dtype='int')
        Q = np.zeros(K+1, dtype='int')
        d = np.zeros((2*SIGMA +1, 2*SIGMA+1), dtype='int')

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

        data['N'] = N
        data['M'] = M
        data['q'] = q.tolist()
        data['p'] = p.tolist()
        data['Q'] = Q.tolist()
        data['d'] = d.tolist()
        data['K'] = K
        data['root'] = 0
        data['SIGMA'] = SIGMA
    return data


