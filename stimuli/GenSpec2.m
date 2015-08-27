function spectrum = GenSpec2(n)
% INPUT:  size of the spectrum (nxn), n should be a power of 2
% OUTPUT: shifted 2D complex number spectrum [켷/2...-1,0,1,...(n/2-1)]
%         pseudorandom white noise
%         DC = 0;
%		  The amplitude of each (pos or neg) frequency component: 	A/2
%         The amplitude of each (whole) frequency component: 		A
%         The power of each (pos or neg) frequency component: 		(A/2)^2
%         The power of each (whole) frequency component: 			A^2
%		  The power of DC-component:								A^2
%
% Author   T. Peromaa 

i = sqrt(-1);
Amp = 2;	%5000
HalfAmp = Amp/2;
Power = Amp^2;
Nyqv = n/2;

% kvadrantti 1
	Re = rand(n/2-1)*Amp-HalfAmp;
	Im = sqrt(HalfAmp^2-Re.*Re);
	Im = RandomSign(Im);	
	quadrant1 = Re+Im*i;
	
% kvadrantti 2
	Re = rand(n/2-1)*Amp-HalfAmp;
	Im = sqrt(HalfAmp^2-Re.*Re);
	Im = RandomSign(Im);	
	quadrant2 = Re+Im*i;
	
% kvadrantti 3
	quadrant3 = rot90(rot90(quadrant2));
	quadrant3 = conj(quadrant3);

% kvadrantti 4
	quadrant4 = rot90(rot90(quadrant1));
	quadrant4 = conj(quadrant4);

% asetetaan kvadrantit spektriin
	spectrum(2:n/2,2:n/2) = quadrant1;
	spectrum(2:n/2,n/2+2:n) = quadrant2;
	spectrum(n/2+2:n,2:n/2) = quadrant3;
	spectrum(n/2+2:n,n/2+2:n) = quadrant4;

% k둺itell뒍n spektrin ensimm둰nen rivi: f1=켷/2
	Re = rand(1,n)*Amp-HalfAmp;
	Im = sqrt(HalfAmp^2-Re.*Re);
	Im = RandomSign(Im);	
	row(1:n) = Re+Im*i;
	apu = fliplr(row);
	row(n/2+2:n) = conj(apu(n/2+1:n-1));
	spectrum(1,:) = row;

% k둺itell뒍n f1=0
	Re = rand(1,n)*Amp-HalfAmp;
	Im = sqrt(HalfAmp^2-Re.*Re);
	Im = RandomSign(Im);	
	row = Re+Im*i;
	apu = fliplr(row);
	row(n/2+2:n) = conj(apu(n/2+1:n-1));
	spectrum(n/2+1,:) = row;

% k둺itell뒍n f2=0
	Re = rand(n,1)*Amp-HalfAmp;
	Im = sqrt(HalfAmp^2-Re.*Re);
	Im = RandomSign(Im);	
	column = Re+Im*i;
	apu = flipud(column);
	column(n/2+2:n) = conj(apu(n/2+1:n-1));
	spectrum(:,n/2+1) = column;

% k둺itell뒍n f2=켷/2
	Re = rand(n,1)*Amp-HalfAmp;
	Im = sqrt(HalfAmp^2-Re.*Re);
	Im = RandomSign(Im);	
	column = Re+Im*i;
	apu = flipud(column);
	column(n/2+2:n) = conj(apu(n/2+1:n-1));
	spectrum(:,1) = column;

% k둺itell뒍n erikseen komponentit, joilla ei ole konjugaattia (vaihe=2� eli Re = -HalfAmp?)
	% f1=f2=켷/2
	% f1=켷/2,f2=0
	% f1=0,f2=켷/2 
	% fi=0,f2=0
	
	spectrum(1,1) = -HalfAmp+0*i;
	spectrum(1,n/2+1) = -HalfAmp+0*i;
	spectrum(n/2+1,1) = -HalfAmp+0*i;
	spectrum(n/2+1,n/2+1) = 0+0*i;
	
	