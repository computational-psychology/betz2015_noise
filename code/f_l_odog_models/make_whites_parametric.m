% If you publish the results of running any of these models please cite the
% original LODOG/FLODOG paper:
% Robinson, A., P. Hammon, & V. de Sa. (2007). Explaining brightness 
%    illusions using spatial filtering and local response normalization. 
%    Vision Research, 47, 1631-1644.
% http://csclab.ucsd.edu/~alan/pub/vr2007_flodog/
%
%make_whites_parametric_patch(width,height,patchy, patch_inlay, scale, leftmost_color)
%Return dual-patch whites stimuli, as floats scaled 0-1.
%think of width and height as counts of square blocks of the patch in x,y
%width = number of bars
%height * scale = height of bars in pixels, width/height = aspect ratio
%patchy = size of patch (* scale = in pixels) 
%patch_inlay = number of bars from outside edges inward that gray is placed
%scale = how big each square block is (min = 3)
%bg color = color of leftmost bar
%patch_pixel_offset = number of pixels that test patch is moved to the
%right. 0 for ordinary whites, or larger if different phase test patches
%are desired.
%
% (c) 2007 Alan Robinson, Paul Hammon, Virgina de Sa.

function model = make_whites_parametric_patch(width,height,patchy, patch_inlay, scale, leftmost_color, patch_pixel_offset, param)

patchy = patchy/2;
inverted = leftmost_color;
patch = .5;

for (i = 1:width*scale)
    model(1:height*scale,i) = mod(floor((i-1)/scale),2);
end

if (inverted) % invert bg
    model = 1 - model;
end

model(((height/2) * scale)-patchy*scale:((height/2) * scale)+patchy*scale, ...
   patch_pixel_offset+1+(patch_inlay-1)*scale:(patch_inlay)*scale+patch_pixel_offset) = patch;

patch_inlay_2 = width-patch_inlay;

model(((height/2) * scale)-patchy*scale:((height/2) * scale)+patchy*scale, ...
    patch_pixel_offset+1+patch_inlay_2*scale:(patch_inlay_2+1)*scale+patch_pixel_offset) = patch;

[y x] = size(model);
