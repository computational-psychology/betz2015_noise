function filter = OriFilt(n,low,high,IG,PR,EO,LR)
% PURPOSE:	Generates a spectrum of orientation bandpass/reject filter (POWER, not amplitude)
% INPUT:  	n: 			size of the filter (should be the same as the image size and a power of 2)
%         	low, high:	Orientation limits of the filter (deg)
%		    IG:			I = ideal: low & high included into the spectrum
%           			G = Gaussian: low & high (1/2 power value)
%			PR:			P = Pass
%						R = Reject
%			EO:			E = even
%						O = odd
%			LR:			L = left 
%						R = right
% OUTPUT: 	Shifted complex number spectrum of an orientation bandpass/reject filter
%
% Author   T. Peromaa 

% -----------------------------------------------------------------------------------------------------------------------
% Check the input

	check = 2:1:12;	check = 2.^check;
	if(~any(n==check)),	disp('Filter size (n) should be a power of two');	return;	end
	%if((low<=-180)|(low>180)|(high<=-180)|(high>180)),	disp('Orientation limits should be ]-180..180]');	return;	end
	if ((IG~='I')&(IG~='G')),	disp('IG has only two possible values: I and G');	return;	end
	if ((PR~='P')&(PR~='R')),	disp('PR has only two possible values: P and R');	return;	end
	if ((EO~='E')&(EO~='O')),	disp('EO has only two possible values: E and O');	return;	end
	if ((LR~='L')&(LR~='R')),	disp('LR has only two possible values: L and R');	return;	end
		
% -----------------------------------------------------------------------------------------------------------------------
% Calculate u-frequency

	u = zeros(n,n);
	for(j=1:1:n), u(j,:) = ones(1,n)*(j-n/2-1); end
	
% -----------------------------------------------------------------------------------------------------------------------
% Calculate v-frequency

	v = zeros(n,n);
	for(j=1:1:n), v(:,j) = ones(n,1)*(j-n/2-1); end
	
% -----------------------------------------------------------------------------------------------------------------------
% Orientation: 0¡(right), 90¡(top), ±180¡(left), -90¡(bottom)
% Degrees:  ]-¹..¹]
	
	radians = atan2(v,u);
	degrees = ((radians*180)/pi)-90;
	k = find(degrees<=-180);	degrees(k) = degrees(k)+360;
	
% -----------------------------------------------------------------------------------------------------------------------
% Calculate requested center orientation (+ conjugate orientation) and space constant (Å width)

	center = (low+high)/2;	
	
	centerC = center-180;
	if(centerC<=-180), centerC = centerC+360; end
	if(centerC>180), centerC = centerC-360; end

	SC = abs(center-low);
	
% -----------------------------------------------------------------------------------------------------------------------
% Calculate the distance of each orientation from the requested centre orientation
% Each orientation is addressed in relation to the closer one of the two Fourier-components

	% -------------------------------------------------------------------------------------------------------------------
	% Distance of the "actual" component. 
		
	distance_actual = abs(center-degrees);
	k = find (distance_actual>180); distance_actual(k) = 360-distance_actual(k);
		
	% -------------------------------------------------------------------------------------------------------------------
	% Distance of the complex conjugate.
	
	distance_conj = abs(centerC-degrees);
	k = find (distance_conj>180); distance_conj(k) = 360-distance_conj(k);
	
	distance = min(distance_actual,distance_conj);
		
% -----------------------------------------------------------------------------------------------------------------------
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

% -----------------------------------------------------------------------------------------------------------------------
% correct the conjugates in row 1: f1=±n/2	(f1+ is the correct one)

	CorrectRow = filter(1,n/2+2:n);
	filter(1,2:n/2) = rot90(rot90(CorrectRow));

% -----------------------------------------------------------------------------------------------------------------------
% correct the conjugates in column 1: f2=±n/2 (f2+ is the correct one)	

	CorrectCol = filter(n/2+2:n,1);
	filter(2:n/2,1) = rot90(rot90(CorrectCol));

% -----------------------------------------------------------------------------------------------------------------------
% If the filter is REJECT, revert the values

	if (PR=='R'),	filter = 1-filter;	end

% -----------------------------------------------------------------------------------------------------------------------
% if the filter is ODD, Re=0, Im = gain and Im = -gain for the conjugates

	if (EO=='O'),
		RealPart = zeros(n,n);
		ImagPart = filter;
		
		% divide plane into 2 parts according to the symmetry properties
		mask = ones(n,n);											% Set mask=1 where the sign changes (left or below)
		AvgOri = (low+high)/2;
		Ortogonal = AvgOri-90;										% ]-90..90]
		if(Ortogonal<=-90), Ortogonal = Ortogonal+180; end 
		slope = -tan(Ortogonal*pi/180);								% tan(alfa) = slope
		if (Ortogonal==90), 
			mask(2:n/2,1:n/2) = (ones(n/2-1,n/2))*(-1); 			% special case: x=0
			mask(n/2+2:n,1:n/2) = (ones(n/2-1,n/2))*(-1);
		else
			k = find((u-slope*v)>0);
			mask(k)=(ones(size(k)))*(-1);
			mask(1,:) = ones(1,n);									% do not change row 1
			mask(n/2+1,:) = ones(1,n);								% do not change row n/2+1
			mask(:,1) = ones(n,1);									% do not change column 1
			mask(:,n/2+1) = ones(n,1);								% do not change column n/2+1
		end
		close all;
		
		ImagPart = mask.*ImagPart;			

		ImagPart(1,2:n/2) = -1*(ImagPart(1,2:n/2));					% row 1:		left = negative
		ImagPart(n/2+1,2:n/2) = -1*(ImagPart(n/2+1,2:n/2));			% row n/2+1:	left = negative
		ImagPart(n/2+2:n,1) = -1*(ImagPart(n/2+2:n,1));				% column 1:		bottom = negative
		ImagPart(n/2+2:n,n/2+1) = -1*(ImagPart(n/2+2:n,n/2+1));		% column n/2+1:	bottom = negative
		ImagPart(1,1) = 0;
		ImagPart(1,n/2+1) = 0;
		ImagPart(n/2+1,1) = 0;
		ImagPart(n/2+1,n/2+1) = 0;
		filter = RealPart+ImagPart*sqrt(-1);
	end

% -----------------------------------------------------------------------------------------------------------------------
% if the filter is RIGHT-type, change the sign of all values

	if (LR=='R');
		filter = -1*filter;
	end
