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
function img = opponent2rgb(opp_img, gamma, srgb_flag)
% Converts rgb values into opponent color values.
%
% outputs:
%   opp_img: opponent image
% 
% inputs:
%   img: s/rgb image with values between 0 and 255 or between 0 and 1
%   gamma: gamma value for gamma correction
%   srgb_flag: 0 if img is rgb; 1 if img is srgb




O12=opp_img(:,:,1);
O23=opp_img(:,:,2);
O3=opp_img(:,:,3);

% For intensity-normalized chromatic channel
% O12=O12.*O3;
% O23=O23.*O3;
% 
% img(:,:,1)=O3/3 + O12/2 + O23/6;
% img(:,:,2)=O3/3 - O12/2 + O23/6;
% img(:,:,3)=O3/3 - O23/3;

img(:,:,3)=O3.*(1-O23)/3.0;
img(:,:,2)=(O3-img(:,:,3)-O3.*O12)*0.5;
img(:,:,1)=O3.*O12+img(:,:,2);



% img(:,:,1)=1/3+opp_img(:,:,1).*0.5+opp_img(:,:,2).*1/6;
% img(:,:,2)=1/3-opp_img(:,:,1).*0.5+opp_img(:,:,2).*1/6;
% img(:,:,3)=1/3-opp_img(:,:,2).*1/3;
% 
% img(:,:,1)=img(:,:,1).*opp_img(:,:,3);
% img(:,:,2)=img(:,:,2).*opp_img(:,:,3);
% img(:,:,3)=img(:,:,3).*opp_img(:,:,3);


if srgb_flag
    % perform gamma correction:
    img_sRGB_temp1 = (img*12.92).*(img <= 0.0031308);
    img_sRGB_temp2 = ((1+0.055)*(img.^(1/gamma))-0.055).*(img > 0.0031308);
    img_sRGB       = img_sRGB_temp1 + img_sRGB_temp2;

    img = img_sRGB;
end


% normalise RGB values if necessary:
%if max(img(:)) > 1
%    img = img/255;
%end

img = img*255;

%img = uint8(img);
end
