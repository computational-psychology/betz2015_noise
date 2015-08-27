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
% img=imread('peppers.png');
img=imread('mandril.tif');

figure,imshow (img);


% nPlans=4;

mida_min=4; % Ha de ser potencia de dos. No recomano que sigui 1 ;)
nPlans=floor(log(max(size(img(:,:,1))-1)/mida_min)/log(2)) + 1

window_sizes=[3 6];
nu_0=3;

ind=CIWaM(img, window_sizes, nPlans, 1, 0, nu_0);

figure,imshow(uint8(ind));