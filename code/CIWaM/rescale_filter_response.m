% Code provided by Xavier Otazu. Original can be downloaded from
% http://www.cvc.uab.cat/~xotazu/?page_id=126
%
% If you publish the results of running the CIWaM / BIWaM model, please cite
% the original papers:
%
% for BIWaM:
% Otazu, X., Vanrell, M., & Alejandro Parraga, C. (2008).
% Multiresolution wavelet framework models brightness induction effects.
% Vision research, 48 (5), 733–51.
%
% for CIWaM:
% Otazu, X., Alejandro Parraga, C., & Vanrell, M. (2010).
% Toward a unified chromatic induction model
% Journal of Vision 10(12):5, 1-24
%
function image = rescale_filter_response(response, level)
% Implementation of Mallate Inverse Discrete Wavelet Transform.
%
% outputs:
%   rec: reconstructed image.
%
% inputs:
%   w: cell array of length wlev, containing wavelet planes in 3
%   orientations.
%   c: cell array of length c, containing residual planes.
%   width: width of image to be reconstructed.
%   height: height of image to be reconstructed.

h       = [1/16, 1/4, 3/8, 1/4, 1/16];  % Gabor-like file used in DWT
inv_sum = 1/sum(h);
image   = response;

for s = 1:level-1

    % upsample last residual:
    image = upsample(upsample(image,2)',2)';
    
    % blur vertically with filter:
    prod = 2*symmetric_filtering(image, h')*inv_sum;

    % blur horizontally with filter:
    prod = 2*symmetric_filtering(prod, h)*inv_sum;
    
    % add wavelet plane information to blurred residual:
    image = prod;    
    
end

