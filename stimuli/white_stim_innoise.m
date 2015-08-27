function [stdstim1, stdstim2] = white_stim_innoise(freq, orientation, stimCont, nn, n, nBars)

% White's illusion in bandpassa filtered white noise
% 
% Authors   V. Salmela 
%           T. Peromaa (noise filtering code)
%           T. Betz (changed into parameterizable function, added second
%                   return stimulus with 180deg rotated noise)
%
% Parameters    freq: noise frequency in cpi
%               orientation: mean orientation (deg), set to -1  for isotropic noise!
%               stimCont: grating contrast (negative values change phase)
if nargin < 4
    nn = 512;   % noise mask size in pixels
    n = 300;    % square wave grating, size in pixels
    nBars = 6;  % number of bars
end

% noisemask parameters
frequency = 2/3 * freq * 12.5 * (nn/512);    % low cut off spatial frequency in cycles/image width (sf bandwidth is 1 oct) (image width = noise mask)
oBandW = 30;            % orientation bandwith

%noiseRms = 0;
noiseRms = 0.2;   % rms-contrast; for no noise, set to zero

% stimulus parameters 
patchLoc = 32 * (nn/512);          % pacth x location, +/- centre of image

% calculate parameters and create stimulus
if orientation == -1
else
    orientation = 180-orientation;
end
oLow = orientation - oBandW/2;                      % orientation limits
oHigh = orientation + oBandW/2;

barWidthPx = n/nBars;                               % calculate bar width in pixels

whiteBarLum = 75;                                   % Luminance of the bright bars (arbitrary value)
blackBarLum = 25;                                   % Luminance of the dark bars (arbitrary value)
patchLum = (whiteBarLum+blackBarLum)/2;             % Luminance of the gray patches

% generate square-wave grating 
profile = ones(n,1)*whiteBarLum;
for i=1:2:nBars,
	profile((i-1)*barWidthPx+1:i*barWidthPx) = ones(barWidthPx,1)*blackBarLum;
end;

stimulus1 = profile*ones(1,n);

% Put the gray patches into the square-wave grating & make std and cmp stimuli
grayPatch = ones(barWidthPx,barWidthPx)*patchLum;
	
Ltop = n/2-barWidthPx+1;                       % !!! note that the gray pathces may have to set manually to correct place
Lbottom = Ltop+barWidthPx-1;        % if you change the stimulus size, because of rounding
Lleft = n/2-patchLoc-barWidthPx+1;
Lright = Lleft+barWidthPx-1;

Rtop = n/2+1;
Rbottom = Rtop+barWidthPx-1;
Rleft = n/2+patchLoc+1;
Rright = Rleft+barWidthPx-1;

stimulus1(Ltop:Lbottom,Lleft:Lright) = grayPatch;
stimulus1(Rtop:Rbottom,Rleft:Rright) = grayPatch;

stimulus1b = ones(nn,nn)*patchLum;    
stimulus1b(nn/2-n/2+1:nn/2+n/2,nn/2-n/2+1:nn/2+n/2) = stimulus1;
 
% convert to contrast values -1 0 +1
avgLum1 = mean(mean((stimulus1b)));
stimulus1b = (stimulus1b-avgLum1)/avgLum1;    

% Create noise mask
f = FreqFilt(nn,frequency,frequency*2,'G','P','E','+');
o = OriFilt(nn,oLow,oHigh,'G','P','E','L');

if orientation == -1
    const = (noiseRms)*nn^2/(sqrt(sum(f(:).^2)));   
else
    const = (noiseRms*2.375)*nn^2/(sqrt(sum(f(:).^2)));   
end

%Create random noise mask 
s = GenSpec2(nn);
if orientation == -1
	sf = s.*f.*const;
else
    sf = s.*f.*o.*const;
end

fsf = fftshift(sf);
Y = ifft2(fsf);
noisemask = real(Y);

% add noise to the stimulus
stdstim1 = .5 * (stimulus1b*stimCont*2+noisemask) + .5;
stdstim2 = .5 * (stimulus1b*stimCont*2+noisemask(end:-1:1,end:-1:1)) + .5;
    
end
