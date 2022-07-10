    print("Travel distance (" + str(num_results) +") :" + str(s))
    print("Path: ")
    for i in range(1, K+1):
        path = ['0']
        v = Y[i]
        while (v):
            path.append(str(v))
            v = X[v]
        path.append('0')
        print("Car" + str(i) + " : " + '-'.join(tuple(path)))