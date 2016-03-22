import os
import numpy as np
from utils import *

# 501 is low dense
np_sec = np.load(open('./numpy/4860.numpy', 'rb'))
plot_seq(np_sec)
