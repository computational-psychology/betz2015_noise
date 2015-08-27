% generate 25 noise masks at all frequencies for model testing. only first 5
% are required for psychophysical experiment.
for noise_freq = round(2 .^ (-log2(9):log2(9)/4:log2(9)) .* 100) ./ 100
    if noise_freq > 2
        noise_max = .43;
        noise_min = -.43;
    else
        noise_max = .4;
        noise_min = -.4;
    end
    
    ppd = 31.2770941620795;
    mask_size = 512;
            
    for k = 1:25
        noise = narrowband_noise(noise_freq, mask_size, ppd, .2, noise_max, noise_min);
        save(sprintf('../noise/noise%i_%1.0fppd_%.2f_%d.mat', mask_size, ppd, noise_freq, k), 'noise')
    end
end
