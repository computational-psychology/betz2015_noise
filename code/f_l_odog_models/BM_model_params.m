% If you publish the results of running any of these models please cite the
% original LODOG/FLODOG paper:
% Robinson, A., P. Hammon, & V. de Sa. (2007). Explaining brightness 
%    illusions using spatial filtering and local response normalization. 
%    Vision Research, 47, 1631-1644.
% http://csclab.ucsd.edu/~alan/pub/vr2007_flodog/

% model settings: (note, not all used, some are just to double check calculations)
% (c) 2007 Alan Robinson, Paul Hammon, Virgina de Sa.
% edited by Torsten Betz to allow for flexibly setting degree per pixel,
% and changed stimulus size to (512, 512)


orientations = 0:30:179;    % 6 steps of 30 degrees
freqs = 0 : 1 : 6;          % 7 different mechanisms

% conversion factors
% original value of Robinson et al
if ~exist('PIXELS_PER_DEGREE', 'var')
    DEG_PER_PIXEL = 0.03125;
else
    DEG_PER_PIXEL = 1 ./ PIXELS_PER_DEGREE;
end


SPACE_CONST_TO_WIDTH = 2 * sqrt(log(2));
SPACE_CONST_TO_STD = 1 / sqrt(2);
STD_TO_SPACE_CONST = 1 / SPACE_CONST_TO_STD;
   
space_const = 2.^freqs * 1.5; % in pixels

std = space_const .* SPACE_CONST_TO_STD; % in pixels

% matches Table 1 in BM(1999)
space_const_deg = space_const * DEG_PER_PIXEL; % in deg.

% compute the standard deviations of the different Gaussian in pixels
space_const = 2.^freqs * 1.5; % space constant of Gaussians
stdev_pixels = space_const .* SPACE_CONST_TO_STD; % in pixels

% (almost matches) points along x-axis of Fig. 10 BM(1997)
cpd = 1 ./ (2 * space_const_deg * SPACE_CONST_TO_WIDTH);

% (almost matches) points along y-axis of Fig. 10 BM(1997)
w_val = cpd .^ 0.1;

% CSF as proposed by Manos and Sakrison
% J. L. Mannos, D. J. Sakrison, 
% "The Effects of a Visual Fidelity Criterion on the Encoding of Images", 
%IEEE Transactions on Information Theory, pp. 525-535, Vol. 20, No 4, (1974) 
CSF = 2.6 * (0.0192 + 0.114 .* cpd) .* exp(-0.114 .* cpd) .^ 1.1;

% model size (changed from (1024x1024)
model_y = 512;
model_x = 512;
