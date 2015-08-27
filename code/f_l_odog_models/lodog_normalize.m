% If you publish the results of running any of these models please cite the
% original LODOG/FLODOG paper:
% Robinson, A., P. Hammon, & V. de Sa. (2007). Explaining brightness 
%    illusions using spatial filtering and local response normalization. 
%    Vision Research, 47, 1631-1644.
% http://csclab.ucsd.edu/~alan/pub/vr2007_flodog/
%
% INPUT: filter_response - a cell array of filter responses,
%         sig1 - standard deviation of local window, along the main axis of the filter
%         sr - ratio of the width of the local window perpendicular to the axis of the filter
%
% OUTPUT: modelOut - the output of the model with normalization by orientation
%
% (c) 2007 Alan Robinson, Paul Hammon, Virgina de Sa.
function modelOut = BM_odog_normalize(filter_response, sig1, sr)

disp('weighting and normalizing');

BM_model_params;

add_const = 10^(-6);     % small additive constant to prevent div by 0 (or other really small values)

% to hold model output
modelOut = 0;

disp('using local normalization by orientation');

% loop over the orientations
for o = 1 : length(orientations)

    this_norm = 0;
    disp('Normalizing...');

    % loop over spatial frequencies
    for f = 1 : length(stdev_pixels)

        % get the filtered response
        filt_img = filter_response{o, f};

        % create the proper weight

         this_norm = this_norm  + filt_img * w_val(f);
    end

        % do local normalization by orientation

        % square
        img_sqr = this_norm .^ 2;

        % sig1= size of gaussian window in the direction of the filter
        % sig2= size of guassian window perpendicular to filter
        sig2 = sig1 * sr;

        % directed along main axis of filter
        rot = orientations(o) * pi/180;

        % create a unit volume gaussian for filtering
        mask = d2gauss(model_x, sig1, model_y, sig2, rot);
        mask = mask ./ sum(mask(:));

        % filter the image (using unit-sum mask --> mean)
        filter_out = ourconv(img_sqr, mask, 0);

        % make sure there are no negative numbers due to fft inaccuracies.
        filter_out = filter_out +10^(-6);

        % take the square root, last part of doing RMS
        filter_out = filter_out .^ 0.5;

        % divide through by normalized image, with additive const

        this_norm = this_norm ./ (filter_out + add_const);


        % accumulate the output
        modelOut = modelOut + this_norm;
    end
end

