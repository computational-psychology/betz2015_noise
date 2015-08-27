function noisemask = narrowband_noise(freq, mask_size, ppd, noiseRms, max_noise, min_noise)

% bandpass filtered white noise, centered on zero, that can be added to a
% stimulus. based on white_stim_innoise.m, but reduced to producing the noise
% mask.
%
% Authors   T. Betz
%           V. Salmela (white_stim_innoise.m)
%           T. Peromaa (noise filtering code)
%
%
if nargin < 2
    mask_size = 512;
    ppd = 31.277;
    noiseRms = .2;
    % we need to set limits on the noise to avoid that stimulus plus noise
    % leaves the range (0,1). The limits depend on the stimulus contrast we
    % want to use. For stim contrast .2, the grating bars will be at .4 and
    % .6, so the noise must not be larger than .4 in any direction.
    max_noise = .4;
    min_noise = -.4;
end

% noisemask parameters
frequency = 2/3 * freq / ppd * mask_size;    % low cut off spatial frequency in cycles/image width (sf bandwidth is 1 oct) (image width = noise mask)

nn = 2 ^ ceil(log2(mask_size));

% Create noise mask
f = FreqFilt(nn,frequency,frequency*2,'G','P','E','+');

const = (noiseRms)*nn^2/(sqrt(sum(f(:).^2)));

%Create random noise mask
max_val = 2;
min_val = -2;
% create noisemask until the extreme values are within desired range
while (max_val > max_noise || min_val < min_noise)
    s = GenSpec2(nn);
    sf = s.*f.*const;
    fsf = fftshift(sf);
    Y = ifft2(fsf);
    noisemask = real(Y);
    % we need to divide the noise mask by two to achieve the same contrast
    % level that Salmela and Laurinen call RMS contrast, because their RMS
    % contrast is normalized by mean luminance, which is 0.5
    noisemask = noisemask ./ 2;
    if nn ~= mask_size
        noisemask = noisemask(1:mask_size, 1:mask_size);
    end
    max_val = max(noisemask(:));
    min_val = min(noisemask(:));
end
end
