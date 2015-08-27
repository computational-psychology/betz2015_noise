#!/usr/bin/python
# -*- coding: latin-1 -*-

from __future__ import division
import numpy as np
import matplotlib.pyplot as plt

from scipy.ndimage.filters import gaussian_laplace
from scipy.misc import imresize

def phaserand(stim, lower, upper):
    Y, X = np.ogrid[-256 : 256, -256 : 256]
    radius = (X ** 2 + Y ** 2) ** .5
    image_fft = np.fft.fftshift(np.fft.fft2(stim))
    amp = np.abs(image_fft)
    phase = np.angle(image_fft)
    phase_shuffled = phase.copy()
    idx = (radius > lower) & (radius <= upper)
    phase_shuffled[idx] = np.random.random(np.sum(idx)) * 2 * np.pi - np.pi
    image_shuffled = amp * np.exp(1j * phase_shuffled)
    return np.real(np.fft.ifft2(np.fft.ifftshift(image_shuffled)))

stim_orig = plt.imread('../figures/che.png')
stim = -gaussian_laplace(stim_orig, 2)
stim -= stim.mean()
plt.imsave('../figures/che_coc.png', stim, vmin = -.2, vmax=.2, cmap='gray')

high_shuffled = phaserand(stim, 30, 512)
plt.imsave('../figures/che_high.png', high_shuffled, vmin = -.2, vmax=.2, cmap='gray')
low_shuffled = phaserand(stim, 0, 30)
plt.imsave('../figures/che_low.png', low_shuffled, vmin = -.2, vmax=.2, cmap='gray')
very_low_shuffled = phaserand(stim, 0, 6)
plt.imsave('../figures/che_verylow.png', very_low_shuffled, vmin = -.2, vmax=.2, cmap='gray')
