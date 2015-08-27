% If you publish the results of running any of these models please cite the
% original LODOG/FLODOG paper:
% Robinson, A., P. Hammon, & V. de Sa. (2007). Explaining brightness 
%    illusions using spatial filtering and local response normalization. 
%    Vision Research, 47, 1631-1644.
% http://csclab.ucsd.edu/~alan/pub/vr2007_flodog/
%
%    filtdog makes a Difference of Gaussians filter

%     r,c: # of rows and columns

%     rf,cf: row and column stds (space constant)

%     sr (spread ratio):  wide spatial spread / narrow one

%     rotate by theta (radians)

function result =  dog(r, c, rf, cf, sr, theta)

  result=single(d2gauss(r,rf,c,cf,theta)-d2gauss(r,rf,c,cf*sr,theta)) ;






