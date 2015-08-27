function filter = FreqFilt(n,low,high,IG,PR,EO,OnOff)
% PURPOSE:	Generated a spectrum of bandpass/reject filter (POWER, not amplitude)
% INPUT:  	n: 			size of the filter (should be the same as the image size and a power of 2)
%         	low, high:	Frequency limits of the filter
%		    IG:			I = ideal: low & high included into the spectrum
%           			G = Gaussian: low & high (1/2 power value)
%			PR:			P = Pass
%						R = Reject
%			EO:			E = even
%						O = odd	(does not make any sense in symmetrical filter)
%			OnOff:		+ = on-center
%						- = off-center
% OUTPUT: 	Shifted complex number spectrum of a bandpass/reject filter
%
% Author   T. Peromaa 


% Check the input
	check = 2:1:12;	check = 2.^check;
	if(~any(n==check)),	disp('Filter size (n) should be a power of two');	return;	end
	if ((IG~='I')&(IG~='G')),	disp('IG has only two possible values: I and G');	return;	end
	if ((PR~='P')&(PR~='R')),	disp('PR has only two possible values: P and R');	return;	end
	if ((EO~='E')&(EO~='O')),	disp('EO has only two possible values: E and O');	return;	end
	if ((OnOff~='+')&(OnOff~='-')),	disp('OnOff has only two possible values: + and -');	return;	end
	
	if(EO=='O'),	disp('€ Circularly symmetric ODD filter does not make sense...');	end
		
% Calculate u-frequency
	u = zeros(n,n);
	for(j=1:1:n), u(j,:) = ones(1,n)*(j-n/2-1); end
	
% Calculate v-frequency
	v = zeros(n,n);
	for(j=1:1:n), v(:,j) = ones(n,1)*(j-n/2-1); end

% Calculate 2D spatial frequency
	frequency = (u.^2+v.^2).^(1/2);
	clear u;	clear v;
	
% Calculate requested center frequency and space constant (‰ width)
	center = (low+high)/2;
	SC = center-low;
		
% Calculate the distance of each 2D spatial frequency from the requested centre frequency
	distance = abs(center-frequency);

% Generate the bandpass filter spectrum: either IDEAL or GAUSSIAN
	filter = zeros(n,n);
	
	if (IG=='I'),
		k = find(distance<=SC);	
		filter(k) = ones(size(k));
	else
		% SC is transformed, because it refers to the 1/e and not to the 1/2 value point
			SC = 1/sqrt(log(2))*SC;
			filter = exp(-(distance/SC).^2);	% Graham, Robson & Nachmias (1978)
		% SQRT is used, because the purpose is to filter POWER, not amplitude	
			k = find(filter>0);
			filter(k) = (filter(k)).^(1/2);
	end;

% correct the conjugates in row 1: f1=±n/2	(f1+ is the correct one)
	CorrectRow = filter(1,n/2+2:n);
	filter(1,2:n/2) = rot90(rot90(CorrectRow));

% correct the conjugates in column 1: f2=±n/2 (f2+ is the correct one)	
	CorrectCol = filter(n/2+2:n,1);
	filter(2:n/2,1) = rot90(rot90(CorrectCol));
	
% If the filter is REJECT, revert the values
	if (PR=='R'),	filter = 1-filter;	end

% if the filter is ODD, Re=0, Im = gain and Im = -gain for the conjugates
	if (EO=='O'),
		RealPart = zeros(n,n);
		ImagPart = filter;
		ImagPart(2:n/2,2:n/2) = -1*(ImagPart(2:n/2,2:n/2));			% quadrant: left, top
		ImagPart(n/2+2:n,2:n/2) = -1*(ImagPart(n/2+2:n,2:n/2));		% quadrant: left, bottom
		ImagPart(1,2:n/2) = -1*(ImagPart(1,2:n/2));					% row 1
		ImagPart(n/2+1,2:n/2) = -1*(ImagPart(n/2+1,2:n/2));			% row n/2+1
		ImagPart(2:n/2,1) = -1*(ImagPart(2:n/2,1));					% column 1
		ImagPart(2:n/2,n/2+1) = -1*(ImagPart(2:n/2,n/2+1));			% column n/2+1
		ImagPart(1,1) = 0;
		ImagPart(1,n/2+1) = 0;
		ImagPart(n/2+1,1) = 0;
		ImagPart(n/2+1,n/2+1) = 0;
		filter = RealPart+ImagPart*sqrt(-1);
	end

% if the filter is off-type, change the sign of all values
	if (OnOff=='-');
		filter = -1*filter;
	end
