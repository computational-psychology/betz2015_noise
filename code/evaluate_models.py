from __future__ import division
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import sys
import lmfit

import odog_model as om
import dakin_bex_model as dbm
import biwam
import flodog

from ocupy import datamat
from scipy.io import loadmat

global grating_frequencies
grating_frequencies = {.1: .103,#.098,
                 .2: .196,
                 .4: .391,
                 .8: .782,
                 1.6: 1.564
                 }

def prepare_grating(bar_width, n_bars, idx_check):
    # create square wave grating
    grating = np.ones((bar_width * n_bars, bar_width * n_bars)) * .45
    index = [i + j for i in range(bar_width) for j in
                range(0, bar_width * n_bars, bar_width * 2)]
    grating[index, :] = .55
    # place test squares at appropriate position
    stimulus = np.ones((512, 512)) * .5
    tmp = grating.shape[0] / 2
    stimulus[256-tmp: 256+tmp, 256-tmp: 256+tmp] = grating
    stimulus[idx_check] = .5
    return stimulus

def add_noise(grating, noise_freq, rep, version):
    noise_dir = '../noise'
    noise = loadmat(noise_dir + '/noise512_31ppd_%1.2f_%d.mat' % (noise_freq,
                rep + 1))['noise'].astype('float64')
    # rotate noise mask 180deg on second half of repetitions
    if version == 1:
        noise = noise[::-1, ::-1]
    noise_masked = noise + .5
    stim_in_noise = .5 * (grating+noise_masked)
    return np.fmin(np.fmax(0, stim_in_noise), 1)

# compute results for isotropic noise
def analyze_frequencies():
    noise_frequencies = np.round(2 ** np.arange(-np.log2(9), np.log2(9)+.01,
        np.log2(9) / 4), decimals=2)
    models = ['odog', 'dbm', 'biwam', 'flodog']
    grating_freqs = ['.2', '.4', '.8']
    for model_nr in range(2):
        if model_nr == 0:
            model = om.OdogModel(img_size=(512, 512), pixels_per_degree=31)
        elif model_nr == 1:
            model = dbm.DBmodel(img_size=(512, 512), bandwidth=2)
        elif model_nr == 2:
            model = biwam.Biwam()
        elif model_nr == 3:
            model = flodog.Flodog()
        with open('../data/%s.csv' % models[model_nr], 'w') as result:
            result.write('Trial noise_type coaxial_lum test_lum match_lum' +
                            ' grating_freq grating_contrast noise_freq rep\n')
            trial_nr = 0
            for grating_freq in grating_freqs:
                if grating_freq == '.8':
                    bar_width = 20
                    n_bars = 12
                elif grating_freq == '.4':
                    bar_width = 40
                    n_bars = 6
                elif grating_freq == '.2':
                    bar_width = 80
                    n_bars = 4
                sys.stdout.write('\rgrating frequency: %s' % grating_freq)
                sys.stdout.flush()

                # determine location of incremental and decremental patches
                idx_upper = np.zeros((512, 512), dtype=bool)
                idx_lower = np.zeros((512, 512), dtype=bool)
                idx_upper[256-bar_width:256, 226-bar_width:226] = True
                idx_lower[256:256+bar_width, 286:286+bar_width] = True
                if n_bars % 4 == 0:
                    idx_inc = idx_upper
                    idx_dec = idx_lower
                else:
                    idx_dec = idx_upper
                    idx_inc = idx_lower
                grating = prepare_grating(bar_width, n_bars, (idx_inc |
                    idx_dec))

                for noise_freq in noise_frequencies:
                    for repeat in range(25):
                        for version in [0, 1]:
                            stimulus = add_noise(grating, noise_freq, repeat,
                                    version)
                            output = model.evaluate(stimulus)
                            value_inc = output[idx_inc].mean()
                            value_dec = output[idx_dec].mean()
                            result_line = (('%d global -1.0 0.5 %f %s 0.1 ' +
                                    '%1.2f %d\n') % (trial_nr, value_inc,
                                        grating_freq, noise_freq,
                                        repeat + 25 * version))
                            result.write(result_line)
                            trial_nr += 1
                            result_line = (('%d global 1.0 0.5 %f %s 0.1 ' +
                                    '%1.2f %d\n') % (trial_nr, value_dec,
                                        grating_freq, noise_freq,
                                        repeat - 25 * (version - 1)))
                            result.write(result_line)
                            trial_nr += 1
                # compute result without noise
                output = model.evaluate((grating + .5) * .5)
                value_inc = output[idx_inc].mean()
                value_dec = output[idx_dec].mean()
                result_line = ('%d none -1.0 0.5 %f %s 0.1 0.0 0\n' % (trial_nr,
                    value_inc, grating_freq))
                result.write(result_line)
                trial_nr += 1
                result_line = ('%d none 1.0 0.5 %f %s 0.1 0.0 0\n' % (trial_nr,
                    value_dec, grating_freq))
                result.write(result_line)
                trial_nr += 1

def compute_illusion_strength(data):
    """Compute illusion strength for all noise frequencies. Data should be
    appropriately filtered (one type of noise, one subject)"""
    noise_frequencies = np.unique(data.noise_freq)
    n_freqs = len(noise_frequencies)
    n_reps = len(np.unique(data.rep))
    illusion_strength = np.empty((n_freqs, n_reps))
    for i, data_by_nf in enumerate(data.by_field('noise_freq')):
        increments = [d.match_lum for d in
            data_by_nf[data_by_nf.coaxial_lum == -1].by_field('rep')]
        decrements = [d.match_lum for d in
            data_by_nf[data_by_nf.coaxial_lum == 1].by_field('rep')]
        illusion_strength[i, :] = np.asarray(increments).flatten() - \
                                  np.asarray(decrements).flatten()
    return illusion_strength

def inverted_gaussian(x, center, baseline, width, minimum):
    x = np.log(x)
    center = np.log(center)
    width = np.log(width)
    return baseline - (baseline + minimum) * np.exp(
            -(x - center) ** 2 / ((width / np.sqrt(2 * np.log(2))) ** 2))

def fit_gaussian(data, constrained=False):
    illusion_strength = compute_illusion_strength(data)
    noise_frequencies = np.unique(data.noise_freq)
    n_reps = illusion_strength.shape[1]
    # fit a horizontal line if the data do not have any real dip
    if data.vp[0] in ['dbm', 'odog'] or (data.vp[0] == 'biwam' and
            data.grating_freq[0] == .2):
        model = lmfit.Model(lambda x, baseline: baseline)
        params = lmfit.Parameters()
        params.add('baseline', value=5)
    else:
        params = lmfit.Parameters()
        #params.add('center', value=3)
        params.add('center',
                value=noise_frequencies[np.argmin(illusion_strength.mean(1))],
                max=9, min=.01)
        params.add('width', value=3)
        if constrained:
            minimum = illusion_strength.mean(1).min()
            params.add('baseline', value=5, max=8.8)
            params.add('minimum', value=-minimum, min=-6, max=-minimum+1)
        else:
            params.add('baseline', value=5)
            params.add('minimum', value=5)
        model = lmfit.Model(inverted_gaussian)
    result = model.fit(illusion_strength.ravel(),
                       x=noise_frequencies.repeat(n_reps),
                       params=params)
    return result

def plot_illusion_strength(data, baseline_data, ax, plot_xticks=True):
    """Plot strength of White's illusion per noise frequency"""
    ax.hold(True)
    y_lims = {'odog': (-.5, 7.5),
             'dbm': (-4, 30),
             'flodog': (-.5, 5.5),
             'biwam': (-1.9, 1.9)}
    y_ticks = {'odog': (0, 3, 6),
             'dbm': (-4, 8, 20),
             'flodog': (0, 2, 4),
             'biwam': (-1, 0, 1)}

    # compute baseline effectsize
    baseline_inc = baseline_data[baseline_data.coaxial_lum == -1].match_lum
    baseline_dec = baseline_data[baseline_data.coaxial_lum == 1].match_lum
    baseline_strength = baseline_inc.mean() - baseline_dec.mean()

    illusion_strength = compute_illusion_strength(data)
    noise_frequencies = np.unique(data.noise_freq)
    fit = fit_gaussian(data, constrained=True)
    x_vals = np.linspace(.1, 10, 1000)
    #spline_fit = interpolate.UnivariateSpline(
    #        noise_frequencies, illusion_strength.mean(1), s=19)
    #ax.plot(x_vals, spline_fit(x_vals), color='.4', lw=3, zorder=2)
    xytext = (0, -20)
    try:
        ax.text(.15, -1.7, 'min: %1.2fcpd' % fit.best_values['center'],
                    ha='left',
                    color='.5',
                    fontname='Helvetica', fontsize=8)
        ax.plot(x_vals, fit.eval(x=x_vals), color='.8', lw=3, zorder=1)
    # KeyError is raised if a line and not a Gaussian was fit
    except KeyError:
        pass
    ax.hlines(baseline_strength, 0.1, 10, linestyles='dotted')
    ax.plot(noise_frequencies, illusion_strength.mean(1),
            'k', ls='none', marker='o', mfc='k', mec='k', ms=5, clip_on=False)
    ax.plot(noise_frequencies, illusion_strength,
            'k', ls='none', marker='.', mfc='.2', mec='.2', ms=3, clip_on=False)

    ax.set_xlim(.1, 10)

    ax.set_ylim(y_lims[data.vp[0]])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_position(('outward', 18))
    ax.spines['left'].set_position(('outward', 10))
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    bottom, top = -10, 10
    marker_ypos = bottom - (top - bottom) * .12
    ax.hlines(0, 0.1, 10, linestyles='solid', clip_on=False)
    ax.set_xscale('log')
    #ax.set_xticklabels(['', '', '1', '10'], fontname='Helvetica')
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.set_xticks([.1, 1, 10])
    ax.set_xticks([.2, .3, .4, .5, .6, .7, .8, .9, 2, 3, 4, 5, 6, 7, 8, 9], minor=True)
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.set_xticklabels(['.1', '1', '10'], fontname='Helvetica')
    if not plot_xticks:
        ax.tick_params(axis='x', which='both', bottom='off', top='off',
                labelbottom='off')
    ax.set_yticks(y_ticks[data.vp[0]])
    ax.set_yticklabels(ax.get_yticks(), fontname='Helvetica')

def global_noise_illusion_strength(data):
    """Create figure of illusion strength against noise frequency, for all
    grating frequencies, and including curve fits. Data should come from a
    single observer."""
    assert len(np.unique(data.vp)) == 1
    n_subplots = len(np.unique(data.grating_freq))
    fig = plt.figure(figsize=(3.2, 1.5 * n_subplots))
    gs = matplotlib.gridspec.GridSpec(2 * n_subplots + 1, 2,
            height_ratios=[1, .1] * n_subplots + [.35],
            width_ratios=[.2, 1])
    for j, data_by_gf in enumerate(data.by_field('grating_freq')):
        baseline_data = data_by_gf[data_by_gf.noise_type == 'none']
        data_by_gf = data_by_gf[data_by_gf.noise_type == 'global']
        ax = fig.add_subplot(gs[j * 2, 1], frameon=False)
        plot_xticks = True if j == (n_subplots - 1) else False
        plot_illusion_strength(data_by_gf, baseline_data, ax, plot_xticks)
        ax.plot(grating_frequencies[data_by_gf.grating_freq[0]], 0,
               'r*', mec='r', clip_on=False)
    ax_ylab = fig.add_subplot(gs[:-1, 0], frameon=False)
    ax_ylab.set_xticks([])
    ax_ylab.set_yticks([])
    ax_ylab.text(.0, .5, r'Illusion strength ($cd/m^2$)', ha='left', va='center',
        rotation='vertical', fontname='Helvetica', fontsize=12,
        transform=ax_ylab.transAxes)
    ax_xlab = fig.add_subplot(gs[-1, 1], frameon=False)
    ax_xlab.set_xticks([])
    ax_xlab.set_yticks([])
    ax_xlab.text(.5, 0, r'Noise mask center SF ($cpd$)', ha='center',
        va='bottom', fontname='Helvetica', fontsize=12,
        transform=ax_xlab.transAxes)
    fig.subplots_adjust(left=.05, bottom=.05, top=.95, right=.95, wspace=.25)
    fig.savefig('../figures/'
            'illusion_strength_global_noise_%s.pdf' % data.vp[0])
    plt.close(fig)

def get_model_data(model_name):
    data = datamat.CsvFactory('../data/%s.csv' % model_name)
    data.add_field('vp', [model_name] * len(data))
    data.add_parameter('exp_type', 'fast_matching')

    if model_name == 'biwam':
        data.match_lum *= 88
    else:
        reference_effect = (
                data.match_lum[(data.coaxial_lum==-1) &
                (data.grating_freq==.4) & (data.noise_type=='none')] -
                data.match_lum[(data.coaxial_lum==1) &
                (data.grating_freq==.4) & (data.noise_type=='none')])
        data.match_lum *= (3. / reference_effect)
    return data

if __name__ == "__main__":
    for model_name in ['odog', 'flodog', 'biwam', 'dbm']:
        data = get_model_data(model_name)
        global_noise_illusion_strength(data)
