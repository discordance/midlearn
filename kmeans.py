import os
import numpy as np
from sklearn.cluster import KMeans
from utils import *

files = []
for root, directories, filenames in os.walk('numpy'):
    for filename in filenames:
        files.append(os.path.join(root,filename))

files = [ file for file in files if file.endswith( ('.numpy') ) ]
arr = []
for f in files[0:100]:
    np_sec = np.load(open(f, 'rb'))
    np_sec = np_sec[0:512].reshape(512*7,-1)
    arr.append(np_sec)

biglist = np.array(arr)
nsamples, nx, ny = biglist.shape
train_dataset = biglist.reshape((nsamples,nx*ny))

kmeans = KMeans(n_clusters=8, init='k-means++') # initialization
kmeans.fit(train_dataset)
#print kmeans.predict(train_dataset)

#print str_repeats('100010001100110011101111')
