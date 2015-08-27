function Imag = RandomSign(Im)

% Author   T. Peromaa 
sign = rand(size(Im));

% randomize the sign 
j = find(sign<=0.5);
sign(j) = ones(size(j))*(-1);
j = find(sign>0.5);
sign(j) = ones(size(j))*1;

Im = Im.*sign;

Imag=Im;