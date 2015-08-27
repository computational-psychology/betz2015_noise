% Example of using ODOG, LODOG, or FLODOG models

% Tech notes:
% Requires Matlab 7 and later (uses singles instead of doubles).
% Works best on machines with more than 512MB ram, and doesn't work at all with less
% than 512MB.
% (c) 9-1-2007 Alan Robinson, Paul Hammon, Virgina de Sa.

% Science Notes:

% If you publish the results of running any of these models please cite the
% original LODOG/FLODOG paper:
% Robinson, A., P. Hammon, & V. de Sa. (2007). Explaining brightness 
%    illusions using spatial filtering and local response normalization. 
%    Vision Research, 47, 1631-1644.
% http://csclab.ucsd.edu/~alan/pub/vr2007_flodog/

% Even if you don't use the newer models, keep in mind that
% our implemenation of the ODOG model differs in a few notable ways from
% the B&M 1999 implementation. See Robinson et al (2007) for details...

% License:  Free for academic use. 

run_model = 3; % select a model: 1= odog, 2=lodog, 3 = flodog

tic % note, this will take a while (~ 10 min depending on machine, memory, and model)

% make an image to process, and pad it to the right size using gray pixels (0.5)
% input should be a matrix/image, with each pixel in the range 0 to 1.
illusion = model_pad_patch(make_bm_whites_thick);

filter_response = BM_filter(illusion); % apply ODOG filters to input image

% Next, weight and combine filters to produce final prediction.
% output is the predicted response. 0 = mean gray, range = somewhat
% arbitrary.  We quantify the strength of the predicted illusion by measuring
% it compared to the predicted illusion strength of White's thick.

if (run_model == 1) 
    output = BM_odog_normalize(filter_response);
elseif (run_model == 2)
    output = lodog_normalize(filter_response, ...
        128, ... % normalization window size in pixels (128=4 degrees)
        1); % aspect ratio of window, 1 = round
else
    output = flodog_normalize(filter_response, ...
        4, ... % normalization window size relative to filter being normed (n)
        1, ... % aspect ratio of window, 1 = round
        .5); % weighted sum across freqs (m)
end


ui_mean_response(output, 2); % display the output, and ask user to specify two regions
% for which the mean prediction will be calculated.

figure, plot(1:1024, output(512,:)); % show horizontal cut thru output

toc % show how long it took
