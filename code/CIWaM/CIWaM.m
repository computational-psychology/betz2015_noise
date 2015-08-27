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
function [ind, wp] = CIWaM(img, window_sizes, wlev, gamma, srgb_flag, nu_0)
% returns saliency map for image
%
% outputs:
%   smap: saliency map for image
%   wp:   the responses of the individual filters, for easy inspection of
%   the inner workings of the model. Added by Torsten Betz
%
% inputs:
%   imag: input image
%   window sizes: window sizes for computing relative contrast; suggested 
%   value of [3 6]
%   wlev: # of wavelet levels
%   gamma: gamma value for gamma correction
%   srgb_flag: 0 if img is rgb; 1 if img is srgb
%   nu_0: peak spatial frequency for CSF; suggested value of 4

% convert opponent colour space of colour images:
% adapted by Torsten Betz to automatically deal with pure grayscale images
if ndims(img) == 2
    [ind, wp] = CIWAM_per_channel(img, wlev, nu_0, 'intensity', window_sizes);
else
    opp_img = rgb2opponent(img, gamma, srgb_flag);
    
    % generate ciwam for each channel:
    rec(:,:,1) = CIWAM_per_channel(opp_img(:,:,1),wlev,nu_0,'colour',window_sizes);
    rec(:,:,2) = CIWAM_per_channel(opp_img(:,:,2),wlev,nu_0,'colour',window_sizes);
    rec(:,:,3) = CIWAM_per_channel(opp_img(:,:,3),wlev,nu_0,'intensity',window_sizes);
    
    ind=opponent2rgb(rec, gamma, srgb_flag);
    wp=NaN;

end
end

function [rec, wp] = CIWAM_per_channel(channel,wlev,nu_0,mode,window_sizes)
% returns chromatic induction for channel
%
% outputs:
%   rec: chromatic induction for channel
%   wp:   the responses of the individual filters, for easy inspection of
%   the inner workings of the model. Added by Torsten Betz
%
%
% inputs:
%   channel: opponent colour channel for which chromatic induction will be computed
%   wlev: # of wavelet levels
%   nu_0: peak spatial frequency for CSF; suggested value of 4
%   mode: type of channel i.e. colour or intensity
%   window sizes: window sizes for computing relative contrast; suggested 
%   value of [3 6]

channel = double(channel);
[w wc]  = DWT(channel,wlev);

% for each scale:
for s = 1:wlev
    % for horizontal, vertical and diagonal orientations:
    for orientation = 1:3
           
    	% retrieve wavelet plane:
        ws = w{s,1}(:,:,orientation);

    	% calculate center-surround responses:
        Zctr = relative_contrast(ws,orientation, window_sizes);

        % return alpha values:
        alpha = generate_csf(Zctr, s, nu_0, mode);
        
        % save alpha value:
        wp{s,1}(:,:,orientation) = ws.*alpha;
    end

end

% reconstruct the image using inverse wavelet transform:
rec = IDWT(wp,wc,size(channel,2),size(channel,1));


end

function zctr = relative_contrast(X,orientation,window_sizes)
% returns relative contrast for each coefficient of a wavelet plane
%
% outputs:
%   zctr: matrix of relative contrast values for each coefficient
% 
% inputs:
%   X: wavelet plane
%   window sizes: window sizes for computing relative contrast; suggested 
%   orientation: wavelet plane orientation

center_size   = window_sizes(1);
surround_size = window_sizes(2);

% horizontal orientation:
if orientation == 1
    
    % define center and surround filters:
    hc = ones(1,center_size);
    hs = [ones(1,surround_size) zeros(1,center_size) ones(1,surround_size)];
    
    % compute std dev:
    sigma_cen = imfilter(X.^2,hc.^2,'symmetric')/(length(find(hc==1)));
    sigma_sur = imfilter(X.^2,hs.^2,'symmetric')/(length(find(hs==1)));
    
% vertical orientation:
elseif orientation == 2
    % define center and surround filters:
    hc = ones(center_size,1);
    hs = [ones(surround_size,1); zeros(center_size,1); ones(surround_size,1)];
    
    % compute std dev:
    sigma_cen = imfilter(X.^2,hc.^2,'symmetric')/(length(find(hc==1)));
    sigma_sur = imfilter(X.^2,hs.^2,'symmetric')/(length(find(hs==1)));

% diagonal orientation:
elseif orientation == 3
    % define center and surround filters:
    hc = ceil((diag(ones(1,center_size)) + fliplr(diag(ones(1,center_size))))/4);
    hs = diag([ones(1,surround_size) zeros(1,center_size) ones(1,surround_size)]);
    hs = hs + fliplr(hs);
    
    % compute std dev:
    sigma_cen = imfilter(X.^2,hc.^2,'symmetric')/(length(find(hc==1)));
    sigma_sur = imfilter(X.^2,hs.^2,'symmetric')/(length(find(hs==1)));    
end

r    = sigma_cen./(sigma_sur+1.e-6);
zctr = r.^2./(1+r.^2);

end
