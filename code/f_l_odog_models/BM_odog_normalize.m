% If you publish the results of running any of these models please cite the
% original LODOG/FLODOG paper:
% Robinson, A., P. Hammon, & V. de Sa. (2007). Explaining brightness 
%    illusions using spatial filtering and local response normalization. 
%    Vision Research, 47, 1631-1644.
% http://csclab.ucsd.edu/~alan/pub/vr2007_flodog/
%
% INPUT: filter_response - a cell array of filter responses,
%       
% OUTPUT: modelOut - the output of the ODOG model with normalization by orientation
%
% (c) 2007 Alan Robinson, Paul Hammon, Virgina de Sa.
function modelOut = BM_odog_normalize(filter_response)

disp('ODOG weighting and normalizing');

BM_model_params;

% to hold model output
modelOut = 0;

% loop over the orientations
for o = 1 : length(orientations)

    this_norm = 0;
    disp('.');
    % loop over spatial frequencies
    for f = 1 : length(stdev_pixels)

        % get the filtered response
        filt_img = filter_response{o, f};

        % create the proper weight

        temp = filt_img * w_val(f);

        this_norm = temp + this_norm;
    end
    % do normalization
    this_norm = this_norm ./ sqrt(mean(this_norm(:) .* this_norm(:)));

    % add in normalized image
modelOut = modelOut + this_norm;

end


