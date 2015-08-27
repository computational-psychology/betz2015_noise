% If you publish the results of running any of these models please cite the
% original LODOG/FLODOG paper:
% Robinson, A., P. Hammon, & V. de Sa. (2007). Explaining brightness 
%    illusions using spatial filtering and local response normalization. 
%    Vision Research, 47, 1631-1644.
% http://csclab.ucsd.edu/~alan/pub/vr2007_flodog/
%
% Create the BM filtered images using best guess at BM approach from the '99 BM paper.
% EXCEPT: fft is padded so input images do not wrap around at borders.

% INPUT : image to filter
% OUTPUT: cell array of responses to each of the 42 ODOG filters

% based on original code by Micah Richert
% (c) 2007 Alan Robinson, Paul Hammon, Virgina de Sa.

function [filter_response] = BM_filter(img)


BM_model_params;

disp('generating filters');


% create a cell array to put things into
filter_response = cell(length(orientations), length(stdev_pixels));


% loop over orientations
for o = 1 : length(orientations)
    
    disp(['orientation = ' num2str(o)]);
    
    % loop over frequencies
    for f = 1 : length(stdev_pixels)
        
        % create the filter
        filter = dog(model_y, model_x, stdev_pixels(f), ...
            stdev_pixels(f), 2, orientations(o) * pi/180);   
    
             
        % get filter response and save it
        filter_response{o, f} = ourconv(img, filter, 0.5);  % pad image with gray
        
        clear filter;
    end
    
end
