#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Lightness matching experiment with White's illusion masked by narrowband noise.
Task: luminance adjustment of a square patch to match the brightness of an
equally sized patch embedded in a square wave grating.
"""
### Imports ###

# Package Imports
#from hrl import HRL

# Qualified Imports
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import time
import random
import glob
import Image, ImageFont, ImageDraw

from stimuli import utils

class EndTrial(Exception):
    def __init__(self, match_lum, view_count):
        self.match_lum = match_lum
        self.view_count = view_count

class EndExperiment(Exception):
    def __init__(self, msg=None):
        self.msg = msg

def draw_text(text, bg=.5, text_color=0, fontsize=48):
    """ create a numpy array containing the string text as an image. """

    bg *= 255
    text_color *= 255
    font = ImageFont.truetype(
            "/usr/share/fonts/truetype/msttcorefonts/arial.ttf", fontsize,
            encoding='unic')
    text_width, text_height = font.getsize(text)
    im = Image.new('L', (text_width, text_height), bg)
    draw = ImageDraw.Draw(im)
    draw.text((0,0), text, fill=text_color, font=font)
    return np.array(im) / 255.

def draw_centered(texture):
    y = (768 - texture.hght) / 2
    x = (1024 - texture.wdth) / 2
    texture.draw((x, y))

def waitButton(datapixx, to):
    """wait for a button press for a given time, and return the button identity
    as first element in a tuple to match hrl API. if no button was pressed,
    button identity is None. This function is only needed until
    hrl.inputs.readButton() is fixed"""
    t = time.time()
    while time.time() - t < to:
        btn = datapixx.readButton()
        if btn is None:
            time.sleep(max(0, min(.01, to - time.time() + t)))
            continue
        btn = btn[0]
        if btn == 2: #up
            return ('Up', 0)
        elif btn == 1: #right
            return ('Right', 0)
        elif btn == 8: #down
            return ('Down', 0)
        elif btn == 4: #left
            return ('Left', 0)
        elif btn == 16: #space
            return ('Space', 0)
    return (None, 0)

### Main ###
def create_design(design_fn, grating_freq):
    header = 'grating_ori grating_vals test_lum noise_type noise_freq rep\r\n'
    trials = []
    total_trials = 0
    grating_ori = 'horizontal'
    for repetition in range(10):
        #for test_lum in [.48, .5, .52]:
        for test_lum in [.5]:
            for noise_type in ['horizontal', 'vertical', 'global' , 'none']:
                if grating_freq != '.4444' and noise_type not in ['global',
                        'none']:
                    continue
                noise_freqs =  np.round(2 ** np.arange(-np.log2(9),
                    np.log2(9)+.1, np.log2(9)/4) * 100) / 100
                #if noise_type != 'global':
                if True:
                    # remove trials with lowest noise freq for local noise
                    # trials, because the noise would not fit the mask
                    noise_freqs = noise_freqs[3:]
                if grating_freq == '.1':
                    # remove trials with highest noise freq for low freq
                    # grating, because the noise cannot be displayed
                    noise_freqs = noise_freqs[:-1]
                if noise_type == 'none':
                    noise_freqs = [0]
                for noise_freq in noise_freqs:
                    for grating_vals in ['-1,1', '1,-1']:
                        trials.append((grating_ori, grating_vals,
                                        str(test_lum), noise_type,
                                        '%1.2f' % noise_freq, str(repetition)))
                        total_trials += 1
    random.shuffle(trials)
    with open(design_fn, 'w') as design_file:
        design_file.write(header)
        for trial in trials:
            design_file.write(' '.join(trial) + '\r\n')
    return total_trials

def prepare_files():
    vp_id  = raw_input ('VP Initialen (z.B. mm): ')
    grating_contrast = ''
    while not grating_contrast in [0.1, 0.2]:
        grating_contrast = float(raw_input('Grating contrast [0.1, 0.2]: '))
    grating_freq = ''
    while not grating_freq in ['.1', '.2', '.4', '.8', '1.6']:
        grating_freq = raw_input('Grating Ortsfrequenz [.1, .2, .4, .8, 1.6]: ')

    design_fn = 'design/fast_matching/narrowband_noise_%s_c%1.1f_sf%s.csv' % (
            vp_id, grating_contrast, grating_freq)
    result_dir = 'data/fast_matching/%s/sf_%s/contrast%i' % (vp_id,
            grating_freq, grating_contrast * 10)
    # check if we are resuming with a know subject and take appropriate action
    completed_trials = 0
    if os.access(design_fn, os.F_OK):
        reply = raw_input('Es gibt bereits Daten zu dieser VP. Weiter? (j/n)')
        if reply != 'j':
            raise EndExperiment()
        filecount = -1
        for filecount, fn in enumerate(
                    glob.glob(os.path.join(result_dir, '*%s*.csv' % vp_id))):
            with open(fn) as result_file:
                # first line in the result file is not a trial
                completed_trials -= 1
                for line in result_file:
                    completed_trials += 1
        result_fn = os.path.join(result_dir, 'noise_matching_%s_%d.csv' %
                (vp_id, filecount + 2))
        # count number of trials in design file
        total_trials = -1
        with open(design_fn) as design_file:
            for line in design_file:
                total_trials += 1
        check_fn = 'check_files/fast_matching/%s/sf_%s/contrast%d/noise_matching_%d.csv' % \
            (vp_id, grating_freq, grating_contrast * 10, filecount + 2)
    # if we are not resuming, create design file
    else:
        os.makedirs(result_dir)
        result_fn = os.path.join(result_dir, 'noise_matching_%s_1.csv' % vp_id)
        total_trials = create_design(design_fn, grating_freq)
        check_fn = 'check_files/fast_matching/%s/sf_%s/contrast%d/noise_matching_%d.csv' % \
            (vp_id, grating_freq, grating_contrast * 10, 1)
        os.makedirs(os.path.split(check_fn)[0])
    return (design_fn, result_fn, completed_trials, total_trials, check_fn,
            grating_contrast, grating_freq)

def prepare_grating(grating_ori, grating_vals, check_pos, check_val,
                        bar_width=38, n_bars=6):
    # create square wave grating
    grating = np.ones((bar_width * n_bars, bar_width * n_bars)) * grating_vals[1]
    index = [i + j for i in range(bar_width) for j in
                range(0, bar_width * n_bars, bar_width * 2)]
    if grating_ori == 'vertical':
        grating[:, index] = grating_vals[0]
    elif grating_ori == 'horizontal':
        grating[index, :] = grating_vals[0]
    # place test square at appropriate position
    y, x = check_pos
    grating[y:y+bar_width, x:x+bar_width] = check_val
    return grating

def add_noise(grating, noise_freq, noise_shape, rep, ppd, noise_type):
    if noise_type == 'none':
        noise = np.zeros((noise_shape, noise_shape))
    else:
        noise = np.load('noisemasks/noise%d_%dppd_%1.2f_%d.npy' % (noise_shape,
            ppd, noise_freq, rep % 5 + 1))
    # rotate noise mask 180deg on second half of repetitions
    if rep >= 5:
        noise = noise[::-1, ::-1]
    if noise_type in ['global', 'none']:
        mask = 1
    else:
        mask = np.zeros_like(noise)
        offset = (noise_shape - grating.shape[0]) / 2
        if noise_type == 'horizontal':
            mask_coords1 = ((offset + 3 * 40 - 1, offset + 2.5 * 40 - 1),
                            (offset + 3 * 40 + 1, offset + 3.5 * 40 + 1))
            mask_coords2 = ((offset + 4 * 40 - 1, offset + 2.5 * 40 - 1),
                            (offset + 4 * 40 + 1, offset + 3.5 * 40 + 1))
        elif noise_type == 'vertical':
            mask_coords1 = ((offset + 3 * 40 - 1, offset + 2.5 * 40 - 1),
                            (offset + 4 * 40 + 1, offset + 2.5 * 40 + 1))
            mask_coords2 = ((offset + 3 * 40 - 1, offset + 3.5 * 40 - 1),
                            (offset + 4 * 40 + 1, offset + 3.5 * 40 + 1))
        mask += utils.smooth_window(noise.shape, mask_coords1, 0, 1, 16)
        mask += utils.smooth_window(noise.shape, mask_coords2, 0, 1, 16)
    noise_masked = noise * mask + .5
    stim = np.ones_like(noise) * .5
    y_border = (stim.shape[0] - grating.shape[0]) / 2.
    x_border = (stim.shape[1] - grating.shape[1]) / 2.
    assert y_border == int(y_border)
    assert x_border == int(x_border)
    stim[y_border:-y_border, x_border:-x_border] = grating
    stim_in_noise = .5 * (stim+noise_masked)
    return np.fmin(np.fmax(0, stim_in_noise), 1)

def prepare_check_background(grating_vals):
    # create random checks as background for match patch
    lum_range = np.abs(np.diff(grating_vals))
    checks = np.array(
              [[0, 5, 0, 1, 3, 0],
               [2, 1, 4, 2, 5, 3],
               [3, 2, 1, 3, 4, 1],
               [4, 1, 2, 4, 2, 5],
               [5, 4, 0, 1, 5, 3],
               [0, 3, 5, 0, 4, 2]], dtype=int)

    values = np.linspace(.5 - lum_range, .5 + lum_range, 6)
    # flip horizontally with probability .5
    checks = checks[:, ::np.round(np.random.rand()) * 2 - 1]
    # flip vertically with probability .5
    checks = checks[::np.round(np.random.rand()) * 2 - 1, :]
    checks = values[checks]
    check_bg = np.repeat(np.repeat(checks, 25, 0), 25, 1)
    return check_bg, checks.flatten()

def adjust_loop(match_lum, match_pos, grating, match_bg):
    """ react to button presses and adjust match luminance accordingly for a
    given time period. Return the final adjusted value of match_lum.
    Raises an EndTrial exception if the center button is pressed.
    """
    smlstp = 0.01
    bgstp = 0.05
    fix_inner = hrl.graphics.newTexture(np.ones((1,1)) * .5, 'circle')
    fix_outer = hrl.graphics.newTexture(np.ones((1,1)) * .3, 'circle')
    match_bg.draw(match_bg_loc)
    match_patch = hrl.graphics.newTexture(np.ones((1,1)) * match_lum)
    match_patch.draw(match_pos, (74, 74))
    fix_outer.draw((512, 383.5 + bar_width / 2), (10, 10))
    fix_inner.draw((512, 383.5 + bar_width / 2), (4, 4))
    hrl.graphics.flip(clr=False)
    time.sleep(.7)
    view_count = 0
    while True:
        # show test stimulus
        grating.draw(stim_loc)
        view_count += 1
        hrl.graphics.flip(clr=True)
        time.sleep(.5)
        match_bg.draw(match_bg_loc)
        match_patch = hrl.graphics.newTexture(np.ones((1,1)) * match_lum)
        match_patch.draw(match_pos, (74, 74))
        fix_outer.draw((512, 383.5 + bar_width / 2), (10, 10))
        fix_inner.draw((512, 383.5 + bar_width / 2), (4, 4))
        hrl.graphics.flip(clr=False)
        # Read the next button press
        btn = None
        while not btn == 'Space':
            btn, _ = hrl.inputs.readButton(36000)
            if hrl.inputs.checkEscape():
                raise EndExperiment('escape pressed')
            # Respond to the pressed button
            if btn == 'Up':
                match_lum += bgstp
            elif btn == 'Right':
                match_lum += smlstp
            elif btn == 'Down':
                match_lum -= bgstp
            elif btn == 'Left':
                match_lum -= smlstp
            match_lum = min(max(match_lum, 0), 1)
            match_patch = hrl.graphics.newTexture(np.ones((1,1)) * match_lum)
            match_patch.draw(match_pos, (74, 74))
            hrl.graphics.flip(clr=False)
        if hrl.inputs.checkEscape():
            raise EndExperiment('escape pressed')
        btn2, _ = hrl.inputs.readButton(.3)
        if btn2 == 'Space':
            raise EndTrial(match_lum, view_count)
    if hrl.inputs.checkEscape():
        raise EndExperiment('escape pressed')
    return

def show_break(trial, total_trials):
    hrl.graphics.flip(clr=True)
    lines = [u'Du kannst jetzt eine Pause machen.',
             u' ',
             u'Du hast %d von %d Durchgängen geschafft.' % (trial,
                 total_trials),
             u' ',
             u'Wenn du bereit bist, drücke die mittlere Taste.',
             u' ',
             u'Wenn du zu einem späteren Zeitpunkt weiter machen willst,',
             u'wende dich an den Versuchsleiter.']
    for line_nr, line in enumerate(lines):
        textline = hrl.graphics.newTexture(draw_text(line, fontsize=36))
        textline.draw(((1024 - textline.wdth) / 2,
                       (768 / 2 - (4 - line_nr) * (textline.hght + 10))))
    hrl.graphics.flip(clr=True)
    btn = None
    while btn != 'Space':
        btn, _ = hrl.inputs.readButton(to=3600)
        if hrl.inputs.checkEscape():
            raise EndExperiment('escape pressed')

def run_trial(dsgn, grating_freq, noise_shape, grating_contrast):
    # prepare a test stimulus texture
    grating_vals = [float(v) for v in dsgn['grating_vals'].split(',')]
    grating_vals = .5 + grating_contrast * np.asarray(grating_vals) / 2
    check_pos = (n_bars / 2 * bar_width, (n_bars / 2 - .5) * bar_width)
    grating = prepare_grating(dsgn['grating_ori'],
                              grating_vals,
                              check_pos,
                              float(dsgn['test_lum']),
                              bar_width=bar_width,
                              n_bars=n_bars)
    ppd = 16 if grating_freq == '.1' else 31
    # determine match patch bar indicator pos from original grating size
    noise_freq = float(dsgn['noise_freq'])
    grating = add_noise(grating,
                      noise_freq,
                      noise_shape,
                      int(dsgn['rep']),
                      ppd,
                      dsgn['noise_type'])

    grating = hrl.graphics.newTexture(grating)
    # prepare and draw the matching background for this trial
    match_bg, bg_values = prepare_check_background([.4, .6])
    match_pos = (match_bg_offset + match_bg.shape[1] / 2 - 37,
                 768  / 2 - 37)
    match_bg = hrl.graphics.newTexture(match_bg)

    # initialize match patch with random value, save it to resultdict
    match_lum = (np.random.random() * .2) + .4
    hrl.results['match_initial'] = float(match_lum)
    # place match patch same distance below center as test patch above

    # preload some variables to prepare for our button reading loop.
    t = time.time()
    btn = None

    ### Input Loop ####
    # Until the user finalizes their luminance choice by raising
    # EndTrial
    trial_over = False
    view_count = 0
    while not trial_over:
        try:
            adjust_loop(match_lum, match_pos, grating, match_bg)
        except EndTrial as et:
            match_lum = et.match_lum
            view_count += et.view_count
            # show confirmation screen
            hrl.graphics.flip(clr=True)
            draw_centered(confirmation)
            hrl.graphics.flip(clr=True)
            btn, _ = hrl.inputs.readButton(to=36000.)
            if btn == 'Space':
                trial_over = True
    return match_lum, view_count, bg_values

def main():
    # determine design and result file name
    try:
        (design_fn, result_fn, completed_trials, total_trials, check_fn,
                grating_contrast, grating_freq) = prepare_files()
    except EndExperiment:
        return 0
    result_headers = ['Trial', 'noise_type', 'coaxial_lum', 'test_lum',
                      'match_lum', 'response_time', 'match_initial',
                      'grating_freq', 'grating_contrast', 'noise_freq',
                      'rep', 'view_count']
    global hrl
    hrl = HRL(graphics='datapixx',
              inputs='responsepixx',
              photometer=None,
              wdth=1024,
              hght=768,
              bg=0.5,
              dfl=design_fn,
              rfl=result_fn,
              rhds=result_headers,
              scrn=1,
              lut='lut0to88.csv',
              db = False,
              fs=True)

    # monkey patch to use non-blocking readButton function
    # should be removed once hrl.inputs.readButton is fixed
    hrl.inputs.readButton = lambda to: waitButton(hrl.datapixx, to)

    # set the bar width of the grating. this value determines all positions
    noise_shape = 512
    global bar_width
    global n_bars
    if grating_freq == '1.6':
        bar_width = 10
        n_bars = 24
    elif grating_freq == '.8':
        bar_width = 20
        n_bars = 12
    elif grating_freq == '.4':
        bar_width = 40
        n_bars = 6
    elif grating_freq == '.2':
        bar_width = 80
        n_bars = 4
    elif grating_freq == '.1':
        bar_width = 80
        n_bars = 4
    x_border = (1024 - noise_shape) // 2
    y_border = (768 - noise_shape) // 2
    global match_bg_offset
    match_bg_offset = 80
    global match_bg_loc
    #TODO match bg location is not dynamically set
    match_bg_loc = (match_bg_offset, (768 - 150) / 2)
    global stim_loc
    stim_loc = (x_border, y_border)

    # prepare confirmation texture
    global confirmation
    #confirmation = hrl.graphics.newTexture(draw_text('Quadrat gesehen? Rechts '
    #    'ja, links nein', bg=.5))
    confirmation = hrl.graphics.newTexture(draw_text('Weiter?', bg=.5))

    # show instruction screen
    if completed_trials == 0:
        for i in range(0):
            instructions = plt.imread('instructions/instructions%d.png' %
                                (i + 1))[..., 0]
            instructions = hrl.graphics.newTexture(instructions)
            instructions.draw((0, 0))
            hrl.graphics.flip(clr=True)
            btn = None
            while btn != 'Space':
                btn, _ = hrl.inputs.readButton(to=3600)

        # show test trials
        test_dsgn = [{'noise_type': 'global',
                      'noise_freq': 9,
                      'grating_ori': 'horizontal',
                      'grating_vals': '-1,1',
                      'rep': 6,
                      'test_lum': '0.5'},
                     {'noise_type': 'global',
                      'noise_freq': 3,
                      'grating_ori': 'horizontal',
                      'grating_vals': '1,-1',
                      'rep': 6,
                      'test_lum': '0.6'},
                     {'noise_type': 'global',
                      'noise_freq': 3,
                      'grating_ori': 'horizontal',
                      'grating_vals': '-1,1',
                      'rep': 6,
                      'test_lum': '0.6'},
                     {'noise_type': 'global',
                      'noise_freq': 5.2,
                      'grating_ori': 'horizontal',
                      'grating_vals': '-1,1',
                      'rep': 6,
                      'test_lum': '0.4'},
                     {'noise_type': 'global',
                      'noise_freq': 5.2,
                      'grating_ori': 'horizontal',
                      'grating_vals': '1,-1',
                      'rep': 6,
                      'test_lum': '0.42'}]

        for dsgn in test_dsgn:
            run_trial(dsgn, grating_freq, 512, grating_contrast)

    # show experiment start confirmation
    hrl.graphics.flip(clr=True)
    lines = [u'Die Probedurchgänge sind fertig.',
        u'Wenn du bereit bist, drücke die mittlere Taste.',
        u' ',
        u'Wenn du noch Fragen hast, oder mehr Probedurchgänge',
        u'machen willst, wende dich an den Versuchsleiter.']
    for line_nr, line in enumerate(lines):
        textline = hrl.graphics.newTexture(draw_text(line, fontsize=36))
        textline.draw(((1024 - textline.wdth) / 2,
                       (768 / 2 - (3 - line_nr) * (textline.hght + 10))))
    hrl.graphics.flip(clr=True)
    btn = None
    while btn != 'Space':
        btn, _ = hrl.inputs.readButton(to=3600)

    ### Core Loop ###

    # hrl.designs is an iterator over all the lines in the specified design
    # matrix, which was loaded at the creation of the hrl object. Looping over
    # it in a for statement provides a nice way to run each line in a design
    # matrix. The fields of each design line (dsgn) are drawn from the design
    # matrix in the design file (design.csv).

    start_time = time.time()
    try:
        for trial, dsgn in enumerate(hrl.designs):

            # skip trials that we already had data for
            if trial < completed_trials:
                continue

            # check if we should take a break (every 15 minutes)
            if time.time() - start_time > (60 * 15):
                show_break(trial, total_trials)
                start_time = time.time()

            trial_start = time.time()
            match_lum, view_count, bg_values = run_trial(dsgn, grating_freq,
                    noise_shape, grating_contrast)
            response_time = time.time() - trial_start

            grating_vals = [float(v) for v in dsgn['grating_vals'].split(',')]
            coaxial_lum = grating_vals[(n_bars / 2) % 2]

            # Once a value has been chosen by the subject, we save all relevant
            # variables to the result file by loading it all into the hrl.results
            # dictionary, and then finally running hrl.writeResultLine().
            hrl.results['Trial'] = trial
            hrl.results['test_lum'] = dsgn['test_lum']
            hrl.results['noise_type'] = dsgn['noise_type']
            hrl.results['noise_freq'] = float(dsgn['noise_freq'])
            hrl.results['coaxial_lum'] = coaxial_lum
            hrl.results['response_time'] = response_time
            hrl.results['grating_contrast'] = grating_contrast
            hrl.results['grating_freq'] = grating_freq
            hrl.results['match_lum'] = float(match_lum)
            hrl.results['rep'] = dsgn['rep']
            hrl.results['view_count'] = view_count
            hrl.writeResultLine()

            # write match bg values to file
            with open(check_fn, 'a') as f:
                f.write('%s\n' %','.join('%0.4f' % x for x in bg_values))

            # We print the trial number simply to keep track during an experiment
            print hrl.results['Trial']

    # catch EndExperiment exception raised by pressing escp for clean exit
    except EndExperiment:
        print "Experiment aborted"
    # And the experiment is over!
    hrl.close()
    print "Session complete"

### Run Main ###
if __name__ == '__main__':
    main()
