% If you publish the results of running any of these models please cite the
% original LODOG/FLODOG paper:
% Robinson, A., P. Hammon, & V. de Sa. (2007). Explaining brightness 
%    illusions using spatial filtering and local response normalization. 
%    Vision Research, 47, 1631-1644.
% http://csclab.ucsd.edu/~alan/pub/vr2007_flodog/
%
% make SBC patches with 3 degree gray patchs (1999 bm, page 4368)
% (c) 2007 Alan Robinson, Paul Hammon, Virgina de Sa.

function model = make_sbc_large

patch_degrees = 3;

block_height = 384;
block_width = 512;

block = ones(block_height, block_width);

[y x] = size(block);

p = patch_degrees*32/2;

block(y/2-p:y/2+p, x/2-p:x/2+p) = .5;
model = [block 1 - block];

