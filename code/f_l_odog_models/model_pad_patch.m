% If you publish the results of running any of these models please cite the
% original LODOG/FLODOG paper:
% Robinson, A., P. Hammon, & V. de Sa. (2007). Explaining brightness 
%    illusions using spatial filtering and local response normalization. 
%    Vision Research, 47, 1631-1644.
% http://csclab.ucsd.edu/~alan/pub/vr2007_flodog/
%
% Gray-pad and center an image to make it the proper size (1024 x 1024)
% (c) 2007 Alan Robinson, Paul Hammon, Virgina de Sa.

function padded = model_pad_patch(model)

%insert model into the center of a 1024x1024 grey matrix
[y x] = size(model);
padded(1:1024,1:1024) = single(.5); % small memory footprint
padded((512-y/2)+1 : (512+y/2), (512-x/2)+1 : (512+x/2)) = (model); 