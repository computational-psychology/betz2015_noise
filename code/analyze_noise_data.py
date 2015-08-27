#!/usr/bin/python
# -*- coding: latin-1 -*-

from __future__ import division
import os
import numpy as np
import matplotlib
import lmfit
import matplotlib.pyplot as plt
from ocupy import datamat
from scipy.stats.stats import pearsonr
from scipy.optimize import curve_fit
from scipy import interpolate

import evaluate_models

global grating_frequencies
grating_frequencies = {.1: .103,#.098,
                 .2: .196,
                 .4: .391,
                 .8: .782,
                 1.6: 1.564
                 }

def plot_lightness_matches(ax, data, connected=False, highlight_unseen=False):
    n_reps = max(data.rep) + 1
    n_freqs = len(np.unique(data.noise_freq))
    point_pairs = np.empty((2, n_reps, n_freqs))
    point_xvals = np.empty((2, n_reps, n_freqs))
    for i, by_coaxial in enumerate(data.by_field('coaxial_lum')):
        color = '.75' if by_coaxial.coaxial_lum[0] == 1 else '.25'
        x_offset = .95 if by_coaxial.coaxial_lum[0] == 1 else 1 / .95
        means = [d.match_lum.mean() for d in by_coaxial.by_field('noise_freq')]
        stds = np.array([d.match_lum.std() / len(d) ** .5 for d in
                    by_coaxial.by_field('noise_freq')])
        ax.plot(np.unique(by_coaxial.noise_freq), means, 's',
                mec=color, mfc=color)
        for j, by_lum in enumerate(by_coaxial.by_field('noise_freq')):
            points = np.asarray([by_rep.match_lum for
                        by_rep in by_lum.by_field('rep')])
            point_pairs[i, :, j] = points.flatten()
            point_xvals[i, :, j] = by_lum.noise_freq[0] * x_offset
            x_vals = np.ones_like(points) * by_lum.noise_freq[0] * x_offset
            ax.plot(x_vals, points, '.', color=color)
            if highlight_unseen:
                by_lum = by_lum[by_lum.patch_visible==0]
                if len(by_lum) == 0:
                    continue
                points = np.asarray([by_rep.match_lum for
                            by_rep in by_lum.by_field('rep')])
                x_vals = np.ones_like(points) * by_lum.noise_freq[0] * x_offset
                ax.plot(x_vals, points, '.', color='r')
    if connected:
        ax.plot(point_xvals.reshape((2, -1)), point_pairs.reshape((2, -1)),
                color='.5', lw=.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    ax.set_xscale('log')
    ax.set_xlim(.096, 10.2)
    ax.set_xscale('log')
    ax.set_xticklabels(['', '', '.1', '1', '10'], fontname='Helvetica')
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.set_ylim([30, 58])
    dark_bar = .5 - data.grating_contrast[0] / 2
    light_bar = .5 + data.grating_contrast[0] / 2
    ax.set_yticks((dark_bar * 88, .5 * 88, light_bar * 88))
    ax.set_yticklabels((dark_bar * 88, 44, light_bar * 88), fontname='Helvetica',
            fontsize=10)
    ax.set_ylabel(r'Match luminance ($cd/m^2$)', fontname='Helvetica',
            fontsize=12)
    ax.hlines(np.array((dark_bar, light_bar, .5)) * 88, .1, 10,
        linestyles=['solid', 'solid', 'solid'],
        linewidths=[.5, .5, .5],
        color=['.2', '.2', '.2'])

def get_all_data(exp_type='fast', vp_names=None, clean=False):
    datadir = '../exp_data'

    if vp_names is None:
        vp_names = [vp_name for vp_name in os.listdir(datadir) if os.path.isdir(
                    os.path.join(datadir, vp_name))]
    all_data = []
    for vp in vp_names:
        grating_freqs = os.listdir(os.path.join(datadir, vp))
        for sf in grating_freqs:
            contrasts = os.listdir(os.path.join(datadir, vp, sf))
            for contrast in contrasts:
                filenames = os.listdir(os.path.join(datadir, vp, sf, contrast))
                data = datamat.CsvFactory(os.path.join(datadir, vp, sf,
                    contrast, filenames[0]))
                for filename in filenames[1:]:
                    data.join(datamat.CsvFactory(os.path.join(datadir, vp, sf,
                        contrast, filename)))
                data.add_field('vp', [vp] * len(data))
                # convert luminance encoding to cd/m^2
                data.match_lum *= 88
                data.match_initial *= 88
                data.test_lum *= 88
                if clean:
                    data = data[~mark_outliers(data)]
                all_data.append(data)
    # combine datamats
    data = all_data[0]
    for this_data in all_data[1:]:
        data.join(this_data)
    data.add_parameter('exp_type', exp_type + '_matching')
    return data

def start_val_correlations(vp, data):
    # create start_lum vs end_lum scatter plots
    fig = plt.figure(figsize=(3,3))
    plt.plot(data.match_initial, data.match_lum, '.k')
    plt.title('r=%.3f, p=%.3f' % pearsonr(data.match_initial,
        data.match_lum))
    plt.ylim((.3*88, .7*88))
    plt.xlim((.3*88, .7*88))
    plt.plot([.3*88, .7*88], [.3*88, .7*88], 'k')
    fig.savefig(
        '../figures/startval_correlation_%s.pdf'
         % vp, bbox_inches='tight', transparent=True)
    plt.close(fig)

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
    return baseline - (baseline - minimum) * np.exp(
            -(x - center) ** 2 / width ** 2)

def fit_gaussian(data, constrained=False):
    illusion_strength = compute_illusion_strength(data)
    noise_frequencies = np.unique(data.noise_freq)
    n_reps = illusion_strength.shape[1]
    # fit a horizontal line if the data do not have any real dip
    # approximate baseline as 3rd largest value
    baseline = np.sort(illusion_strength.mean(1))[-2]
    minimum = illusion_strength.mean(1).min()
    if baseline - minimum < illusion_strength.mean(1).max() - baseline:
        model = lmfit.Model(lambda x, baseline: baseline)
        params = lmfit.Parameters()
        params.add('baseline', value=baseline)
    else:
        params = lmfit.Parameters()
        #params.add('center', value=3)
        params.add('center',
                value=noise_frequencies[np.argmin(illusion_strength.mean(1))],
                max=9, min=.5)
        params.add('width', value=2)
        if constrained:
            params.add('baseline', value=baseline)
            params.add('minimum', value=minimum, min=minimum-1, max=baseline+1)
        else:
            params.add('baseline', value=5)
            params.add('minimum', value=-2)
        model = lmfit.Model(inverted_gaussian)
    result = model.fit(illusion_strength.ravel(),
                       x=noise_frequencies.repeat(n_reps),
                       params=params)
    return result

def plot_illusion_strength(data, baseline_data, ax, plot_xticks=True):
    """Plot strength of White's illusion per noise frequency"""
    ax.hold(True)

    # compute baseline effectsize
    baseline_inc = baseline_data[baseline_data.coaxial_lum == -1].match_lum
    baseline_dec = baseline_data[baseline_data.coaxial_lum == 1].match_lum
    baseline_strength = baseline_inc.mean() - baseline_dec.mean()
    ax.plot([.1145] * len(baseline_inc), baseline_inc - baseline_dec.mean(),
            ls='none', marker='o', mfc='.4', mec='.4', ms=3, clip_on=False)
    ax.plot([.131] * len(baseline_dec), baseline_inc.mean() - baseline_dec,
            ls='none', marker='o', mfc='.1', mec='.1', ms=3, clip_on=False)
    #ax.plot([.1225], baseline_strength,
    #        ls='none', marker='o', mfc='k', mec='k', ms=5, clip_on=False)
    ax.hlines(0, .1, .15, linestyles='solid', clip_on=False)


    illusion_strength = compute_illusion_strength(data)
    noise_frequencies = np.unique(data.noise_freq)
    fit = fit_gaussian(data, constrained=True)
    x_vals = np.linspace(.2, 10, 1000)
    ax.plot(x_vals, fit.eval(x=x_vals), color='.8', lw=3, zorder=1)
    #spline_fit = interpolate.UnivariateSpline(
    #        noise_frequencies, illusion_strength.mean(1), s=19)
    #ax.plot(x_vals, spline_fit(x_vals), color='.4', lw=3, zorder=2)
    xytext = (0, -20)
    try:
        ax.text(.15, -8, 'min: %1.2fcpd' % fit.best_values['center'],
                    ha='left',
                    color='.5',
                    fontname='Helvetica', fontsize=8)
    # KeyError is raised if a line and not a Gaussian was fit
    except KeyError:
        pass
    ax.hlines(baseline_strength, 0.2, 10, linestyles='dotted')
    ax.plot(noise_frequencies, illusion_strength.mean(1),
            'k', ls='none', marker='o', mfc='k', mec='k', ms=5, clip_on=False)
    ax.plot(noise_frequencies, illusion_strength,
            'k', ls='none', marker='o', mfc='.2', mec='.2', ms=3, clip_on=False)

    ax.set_xlim(.1, 10)

    if data.vp[0] == 'n7':
        ax.set_ylim([-30, 30])
    else:
        ax.set_ylim([-15, 17])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_position(('outward', 18))
    ax.spines['left'].set_position(('outward', 10))
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    bottom, top = -10, 10
    marker_ypos = bottom - (top - bottom) * .12
    ax.hlines(0, 0.2, 10, linestyles='solid', clip_on=False)
    ax.set_xscale('log')
    #ax.set_xticklabels(['', '', '1', '10'], fontname='Helvetica')
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.set_xticks([.2, 1, 10])
    ax.set_xticks([.3, .4, .5, .6, .7, .8, .9, 2, 3, 4, 5, 6, 7, 8, 9], minor=True)
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.set_xticklabels(['.2', '1', '10'], fontname='Helvetica')
    if not plot_xticks:
        ax.tick_params(axis='x', which='both', bottom='off', top='off',
                labelbottom='off')
    ax.set_yticks((-8, 0, 8))
    if data.vp[0] == 'n7':
        ax.set_yticks((-16, 0, 16))
    ax.set_yticklabels(ax.get_yticks(), fontname='Helvetica')

def local_noise_illusion_strength(data):
    """Plot illusion strength versus noise frequency for the two local noise
    conditions at medium grating frequency."""
    fig = plt.figure(figsize=(3.2, 3))
    plot_positions = {'vertical': 0, 'horizontal': 1}
    gs = matplotlib.gridspec.GridSpec(5, 2,
            height_ratios=[1, .1, 1, .1, .3],
            width_ratios=[.2, 1])
    baseline_data = data[(data.grating_freq == .4) & (data.noise_type ==
            'none')]
    baseline_strength = baseline_data[baseline_data.coaxial_lum ==
            -1].match_lum.mean() - baseline_data[baseline_data.coaxial_lum ==
                    1].match_lum.mean()
    data = data[(data.noise_type == 'horizontal') | (data.noise_type ==
        'vertical')]
    for data_by_noiseori in data.by_field('noise_type'):
        j = plot_positions[data_by_noiseori.noise_type[0]]
        ax = fig.add_subplot(gs[j * 2, 1], frameon=False)
        plot_xticks = True if j == 1 else False
        plot_illusion_strength(data_by_noiseori, baseline_strength, ax, plot_xticks)
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
    fig.savefig('../figures/illusion_strength_local_noise_%s.pdf' % (data.vp[0]))
    plt.close(fig)

def local_noise_matches(data, highlight_unseen=False):
    """Creates and saves figures of lightness matches in the local noise
    condition for all subjects in data."""
    data = data[(data.noise_type == 'horizontal') | (data.noise_type ==
        'vertical')]
    for vp_data in data.by_field('vp'):
        for current_data in vp_data.by_field('noise_type'):
            for plot_lines in [0,1]:
                fig, ax = plt.subplots(figsize=(5, 4))
                plot_lightness_matches(ax, current_data, connected=plot_lines,
                        highlight_unseen=highlight_unseen)
                fig.savefig('../figures/'
                        '%s_lightness_matches_%s_%s.pdf' % (
                            current_data.noise_type[0], ['', 'connected']
                            [plot_lines], current_data.vp[0]))
                plt.close(fig)

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
    fig.savefig('../figures/illusion_strength_global_noise_%s.pdf' %
            (data.vp[0]))
    plt.close(fig)

def global_noise_matches(data, highlight_unseen=False):
    """Creates and saves figures of lightness matches in the global noise
    condition for all subjects in data."""
    #data = data[data.noise_type == 'global']
    if highlight_unseen:
        data.match_lum.mask = data.patch_visible == 0
    for vp_data in data.by_field('vp'):
        for contrast_data in vp_data.by_field('grating_contrast'):
            for current_data in contrast_data.by_field('grating_freq'):
                for plot_lines in [0,1]:
                    fig, ax = plt.subplots(figsize=(5, 4))
                    plot_lightness_matches(ax, current_data, connected=plot_lines,
                            highlight_unseen=highlight_unseen)
                    fig.savefig('../figures/'
                            '%slightness_matches%s_%1.1f_%s.pdf' %
                            (['', 'unseen_masked/'][int(highlight_unseen)],
                                ['', '_connected'][plot_lines],
                                current_data.grating_freq[0],
                                current_data.vp[0]))
                    plt.close(fig)

def compute_slope(data):
    """Compute the slope of the function relating changes in grating frequency
    to changes in the most effective noise frequency."""

    #compute slopes for observers
    all_dips = np.full((3, 8), np.nan)
    grating_freqs = [grating_frequencies[gf] for gf in
                        np.unique(data.grating_freq)]
    grating_freqs.sort()
    for i, vp_data in enumerate(data.by_field('vp')):
        for j, freq_data in enumerate(vp_data.by_field('grating_freq')):
            if freq_data.vp[0] == 'n4' and freq_data.grating_freq[0]==.2:
                continue
            fit = fit_gaussian(freq_data, constrained=True)
            try:
                all_dips[j, i] = fit.best_values['center']
            except KeyError:
                pass
    all_dips = np.ma.MaskedArray(all_dips, np.isnan(all_dips))
    slope_low = (all_dips[1] / all_dips[0]).mean() / (grating_freqs[1] /
            grating_freqs[0])
    slope_high = (all_dips[2] / all_dips[1]).mean() / (grating_freqs[2] /
            grating_freqs[1])
    # bootstrap slopes
    slope_dist_low = np.full(10000, np.nan)
    slope_dist_high = np.full(10000, np.nan)
    for i in xrange(10000):
        ratio_low = (all_dips[1] / all_dips[0]).compressed()
        ratio_high = (all_dips[2] / all_dips[1]).compressed()
        slope_dist_low[i] = np.random.choice(ratio_low, len(ratio_low)).mean()
        slope_dist_high[i] = np.random.choice(ratio_high, len(ratio_high)).mean()
    slope_dist_low /= (grating_freqs[1] / grating_freqs[0])
    slope_dist_high /= (grating_freqs[2] / grating_freqs[1])



    # compute slope for models
    model_dips = np.full((2, 2), np.nan)
    biwam = evaluate_models.get_model_data('biwam')
    flodog = evaluate_models.get_model_data('flodog')
    for i, model_data in enumerate([biwam, flodog]):
        model_data = model_data[model_data.grating_freq!=.2]
        for j, freq_data in enumerate(model_data.by_field('grating_freq')):
            fit = evaluate_models.fit_gaussian(freq_data, constrained=True)
            try:
                model_dips[j, i] = fit.best_values['center']
            except KeyError:
                pass
    slope_biwam = model_dips[1, 0] / model_dips[0, 0] / (grating_freqs[2] /
                        grating_freqs[1])
    slope_flodog = model_dips[1, 1] / model_dips[0, 1] / (grating_freqs[2] /
                        grating_freqs[1])

    return (slope_low, slope_high, slope_dist_low, slope_dist_high,
            slope_biwam, slope_flodog)

def grating_freq_vs_dip_freq(data):
    """Plot the most effective noise frequency against grating frequency"""
    #colors = ['#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5',
    #            '#08519c', '#08306b']
    colors = ['#9ecae1'] * 8
    model_colors = ['#e41a1c', '#4daf4a']
    data = data[data.noise_type=='global']
    fig, ax = plt.subplots(figsize=(3,3))
    all_dips = np.full((3, 8), np.nan)
    for i, vp_data in enumerate(data.by_field('vp')):
        grating_freqs = [grating_frequencies[gf] for gf in
                            np.unique(vp_data.grating_freq)]
        grating_freqs.sort()
        dip_frequencies = np.full(len(np.unique(vp_data.grating_freq)), np.nan)
        for j, freq_data in enumerate(vp_data.by_field('grating_freq')):
            fit = fit_gaussian(freq_data, constrained=True)
            try:
                dip_frequencies[j] = fit.best_values['center']
                all_dips[j, i] = fit.best_values['center']
            except KeyError:
                pass
        ax.plot(grating_freqs, dip_frequencies, marker='o', ms=3, ls='-',
                lw=1, color=colors[i], mec='none', clip_on=False, zorder=100)
    ax.plot(grating_freqs, np.nanmean(all_dips, 1), marker='o', ms=6, ls='-',
            lw=2, color='#08519c', mec='none', clip_on=False, zorder=101)
    ax.text(1, np.nanmean(all_dips[2,:]), 'observers',
            fontname='Helvetica', fontsize=12, color='#08519c')
    # include model results
    biwam = evaluate_models.get_model_data('biwam')
    flodog = evaluate_models.get_model_data('flodog')
    for i, model_data in enumerate([biwam, flodog]):
        model_data = model_data[model_data.grating_freq!=.2]
        grating_freqs = [grating_frequencies[gf] for gf in
                            np.unique(model_data.grating_freq)]
        grating_freqs.sort()
        dip_frequencies = np.full(len(np.unique(model_data.grating_freq)), np.nan)
        for j, freq_data in enumerate(model_data.by_field('grating_freq')):
            fit = evaluate_models.fit_gaussian(freq_data, constrained=True)
            try:
                dip_frequencies[j] = fit.best_values['center']
            except KeyError:
                pass
        ax.plot(grating_freqs, dip_frequencies, marker='o', ms=6, ls='-',
                lw=2, color=model_colors[i], mec='none', clip_on=False, zorder=100)
        ax.text(1, dip_frequencies[1], ['BIWAM', 'FLODOG'][i],
                fontname='Helvetica', fontsize=12, color=model_colors[i])

    # plot diagonal lines with constant spacing
    for x in (.1 * 2 ** np.arange(0, 7)):
        ax.plot((x, x * 100), (.1, 10.1), ls="-", c=".7", lw=.5)
        ax.plot((.1, 10.1), (x, x * 100), ls="-", c=".7", lw=.5)
    ax.set_ylim((.1, 10))
    ax.set_xlim((.1, 10))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['bottom'].set_position(('outward', 5))
    ax.spines['left'].set_position(('outward', 5))
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    ax.set_xscale('log')
    ax.set_xticklabels(['', '.1', '1', '10'], fontname='Helvetica')
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.set_yscale('log')
    ax.set_yticklabels(['', '.1', '1', '10'], fontname='Helvetica')
    ax.set_ylabel(r'Noise mask center SF ($cpd$)', fontname='Helvetica',
            fontsize=12)
    ax.set_xlabel(r'Grating spatial frequency ($cpd$)', fontname='Helvetica',
            fontsize=12)
    fig.savefig('../figures/grating_freq_vs_dip_freq.pdf',
            bbox_inches='tight')
    plt.close(fig)

if __name__ == '__main__':
    data = get_all_data(clean=False)


    for i, vp_data in enumerate(data.by_field('vp')):
        global_noise_illusion_strength(vp_data)

    # filter out non-standard observers
    data = data[np.in1d(data.vp, ['e1', 'n7', 'n2'], invert=True)]
    data = data[(data.vp!='n4') | (data.grating_freq!=.2)]
    grating_freq_vs_dip_freq(data)
