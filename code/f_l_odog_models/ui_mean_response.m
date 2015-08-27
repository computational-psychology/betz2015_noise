% If you publish the results of running any of these models please cite the
% original LODOG/FLODOG paper:
% Robinson, A., P. Hammon, & V. de Sa. (2007). Explaining brightness 
%    illusions using spatial filtering and local response normalization. 
%    Vision Research, 47, 1631-1644.
% http://csclab.ucsd.edu/~alan/pub/vr2007_flodog/
%
function mean_response(image, regions)
% show image, and ask the user to specify n regions, for which the mean will
% be calculated and printed to console.
% (c) 8-10-2007 Alan Robinson

figure; imagesc(image); axis square; colormap(gray); % show output 

title('click upper left, then click lower right');

for (i=1:regions)
    [x1, y1] = ginput(1); % upper left
    [x2, y2] = ginput(1); % lower right

   tmp = image(ceil(y1):ceil(y2), ceil(x1):ceil(x2));
fprintf('mean of %i region is: %1.3f\n', i, mean(tmp(:)));
end

title('model output');