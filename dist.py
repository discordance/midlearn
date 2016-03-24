from scipy.spatial.distance import *
import numpy as np

XA = np.array(
    [
        [1,0,0,1],
        [0,0,0,0],
        [0,0,0,0],
        [0,0,0,0]
    ]
)
XB = np.array(
    [
        [1,0,0,1],
        [0,0,0,0],
        [0,0,0,0],
        [0,0,0,0]
    ]
)

print cdist(XA, XB, 'euclidean').diagonal()
