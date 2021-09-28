coords = [(0, 0), (0, 1), (1, 0), (1, 1), (0, 2), (1, 2), (0, 3), (1, 3), (2, 2), (2, 3), (3, 2), (2, 1), (3, 1), (3, 3), (4, 2), (5, 2), (4, 1), (4, 3), (5, 3), (6, 2), (5, 1), (6, 1), (6, 3), (7, 2), (8, 2), (7, 1), (7, 3), (8, 3), (9, 2), (8, 1), (8, 4), (9, 3), (7, 4), (8, 5), (9, 4), (9, 5), (7, 5), (8, 6), (8, 7), (9, 6), (7, 6), (8, 8), (9, 7), (7, 7), (8, 9), (9, 8), (7, 8), (7, 9), (6, 8), (6, 7), (6, 9), (5, 8), (4, 8), (5, 9), (5, 7), (4, 9), (3, 8), (4, 7), (3, 7), (3, 9), (2, 8), (2, 9), (1, 8), (2, 7), (1, 7), (1, 9), (0, 8), (0, 7), (1, 6), (2, 6), (0, 6), (1, 5), (2, 5), (1, 4), (0, 5), (2, 4), (3, 5), (4, 5), (3, 4), (3, 6), (4, 4), (5, 5), (4, 6), (5, 4), (5, 6), (6, 5), (6, 6), (6, 4), (6, 0), (7, 0), (5, 0), (8, 0), (9, 0), (9, 1), (4, 0), (3, 0), (2, 0), (0, 4), (0, 9)]
# coords = [(i, j) for j in range(0, 50) for i in range(0, 50)]
def dijkstra(destination, begin):
    paths = {begin: [None, 0]}
    x = 0
    while destination not in paths.keys():
        x += 1
        pathscopy = paths.copy()
        for i in pathscopy.keys():
            next = [(i[0], i[1]+1), (i[0], i[1]-1), (i[0]+1, i[1]), (i[0]-1, i[1])]
            for j in next:
                if j in coords and j not in paths.keys():
                    paths[j] = [i, x]
    shortpath = [destination]
    prev = paths[destination][0]
    while prev:
        shortpath.append(prev)
        prev = paths[prev][0]
    print(shortpath)
    print(paths.keys())
    return shortpath[-2]


print(dijkstra((0, 0), (8, 5)))
# calculating path dict_keys([(0, 8), (0, 7), (0, 9), (1, 8)])
