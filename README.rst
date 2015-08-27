This is the code used to produce the results published in

Betz T, Shapley R, Wichmann F A, Maertens M (2015) Noise masking of White's
illusion exposes the weakness of current spatial filtering models of lightness
perception. Journal of Vision.

The repository contains the following:

-Matlab code for generating noise stimuli, kindly provided by Dr. Salmela, and
 adapted to fit the needs of the present work: [stimuli](stimuli)

-The code for running the experiment ([experiment.py](experiment.py); requires hrl to run).
 Due to the file size, the noise masks themselves are not provided, but can be
 created with [generate_noisemasks.m](stimuli/generate_noisemasks.m)

-The data from the psychophysical experiment: [exp_data](exp_data)

-A script to analyze the experimental data and generate figures:
 [analyze_noise_data.py](code/analyze_noise_data.py)

-Scripts to analyze the different lightness models with noise:
 * [evaluate_models.py](code/evaluate_models.py) to compute model responses for
   ODOG and the Dakin-Bex model, and to create result figures for all models
 * [evaluate_matlab_models.m](code/evaluate_matlab_models.m) to compute
   responses to noise stimuli for BIWAM and FLODOG
 * code for the BIWaM model (CIWaM), kindly provided by Dr. Otazu
 * code for the FLODOG model (f_l_odog_models), kindly provided by Dr. Robinson
 * implementations of the ODOG and Dakin-Bex model are located in a separate
   repository [lightness_models](https://github.com/TUBvision/lightness_models)

-The data from the model simulations: [data](data)

-A script to create the phase shuffled version of the COBC illusion (Figure 12
 in the article): [create_dakin_bex_demo.py](create_dakin_bex_demo.py)

Some of the python scripts require [ocupy](https://github.com/nwilming/ocupy)
to run.

Documentation for the analysis scripts is sketchy, but the models themselves
are well documented.
Get in touch with [Torsten](http://www.cognition.tu-berlin.de/menue/tubvision/people/torsten_betz/)
in case you have questions.
