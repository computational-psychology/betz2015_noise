% If you publish the results of running any of these models please cite the
% original LODOG/FLODOG paper:
% Robinson, A., P. Hammon, & V. de Sa. (2007). Explaining brightness 
%    illusions using spatial filtering and local response normalization. 
%    Vision Research, 47, 1631-1644.
% http://csclab.ucsd.edu/~alan/pub/vr2007_flodog/
%
%same as thick lined whites (2 degree by 4 degree test patches) used in bm
%1999 (see page 4377, 4371)

% INPUT: pixels to ofset patch (optional)

% OUTPUT: white's illusion as grayscale matrix

% Note: this is a more advanced example of making a stimulus, see
% make_bm_sbc_large for a simple example to get started with.
% (c) 2007 Alan Robinson, Paul Hammon, Virgina de Sa.

function model = make_bm_whites_thick(patch_pixel_offset)

eval('patch_pixel_offset;', ' patch_pixel_offset = 0;'); % default val for patch pixel offset
   
model = make_whites_parametric(8, 6, 2, 3, 64, 0, patch_pixel_offset );

