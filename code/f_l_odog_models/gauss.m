% If you publish the results of running any of these models please cite the
% original LODOG/FLODOG paper:
% Robinson, A., P. Hammon, & V. de Sa. (2007). Explaining brightness 
%    illusions using spatial filtering and local response normalization. 
%    Vision Research, 47, 1631-1644.
% http://csclab.ucsd.edu/~alan/pub/vr2007_flodog/
%
% Function "gauss.m": 1-D gaussian
function y = gauss(x,std)
y = exp(-x.^2/(2*std^2)) / (std*sqrt(2*pi));
