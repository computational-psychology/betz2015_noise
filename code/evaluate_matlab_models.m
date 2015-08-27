
%compute results for isotropic noise
function evaluate_matlab_models()
noise_frequencies = round(2 .^ (-log2(9):log2(9)/4:log2(9)) .* 100) ./ 100;
models = {'biwam', 'flodog'};
grating_freqs = {'.2', '.4', '.8'};
for model_nr = 1:2
    
    if model_nr == 2
        PIXELS_PER_DEGREE = 31; %#ok<NASGU> the value is used inside BM_model_params
        BM_model_params;
        filters = cell(length(orientations), length(stdev_pixels));
        for o = 1 : length(orientations)
            % loop over frequencies
            for f = 1 : length(stdev_pixels)
                % create the filter
                filters{o, f} = dog(model_y, model_x, stdev_pixels(f), ...
                    stdev_pixels(f), 2, orientations(o) * pi/180);
            end
        end
        filter_response = cell(length(orientations), length(stdev_pixels));
    end
    
    result = fopen(sprintf('../data/%s.csv', models{model_nr}), 'w');
    fprintf(result, 'Trial noise_type coaxial_lum test_lum match_lum grating_freq grating_contrast noise_freq rep\n');
    trial_nr = 0;
    for grating_freq_nr = 1:3
        grating_freq = grating_freqs{grating_freq_nr};
        if strcmp(grating_freq, '.8')
            bar_width = 20;
            n_bars = 12;
        elseif strcmp(grating_freq, '.4')
            bar_width = 40;
            n_bars = 6;
        elseif strcmp(grating_freq, '.2')
            bar_width = 80;
            n_bars = 4;
        end
        fprintf('\rgrating frequency: %s', grating_freq)
        
        % determine location of incremental and decremental patches
        idx_upper = false(512);
        idx_lower = false(512);
        idx_upper(257-bar_width:256, 227-bar_width:226) = true;
        idx_lower(257:256+bar_width, 287:286+bar_width) = true;
        if mod(n_bars, 4) == 0
            idx_inc = idx_upper;
            idx_dec = idx_lower;
        else
            idx_dec = idx_upper;
            idx_inc = idx_lower;
        end
        
        grating = prepare_grating(bar_width, n_bars, (idx_inc | idx_dec));
        
        for noise_freq = noise_frequencies
            for repeat = 0:24
                for version = 0:1
                    stimulus = add_noise(grating, noise_freq, repeat, version);
                    if model_nr == 1
                        nPlans=floor(log(max(size(stimulus)-1)/4)/log(2)) + 1;
                        output = CIWaM(stimulus, [5,4], nPlans, 1, 0, 2.967);
                    elseif model_nr == 2
                        for o = 1 : length(orientations)
                            % loop over frequencies
                            for f = 1 : length(stdev_pixels)
                                filter_response{o, f} = ourconv(stimulus, filters{o, f}, 0.5);  % pad image with gray
                            end
                        end
                        output = flodog_normalize(filter_response, ...
                            4, ... % normalization window size relative to filter being normed (n)
                            1, ... % aspect ratio of window, 1 = round
                            .5); % weighted sum across freqs (m)
                        
                    end
                    value_inc = mean(output(idx_inc));
                    value_dec = mean(output(idx_dec));
                    fprintf(result, '%d global -1.0 0.5 %f %s 0.1 %1.2f %d\n', ...
                        trial_nr, value_inc, grating_freq, noise_freq, repeat + 25 * version);
                    trial_nr = trial_nr + 1;
                    fprintf(result, '%d global 1.0 0.5 %f %s 0.1 %1.2f %d\n', ...
                        trial_nr, value_dec, grating_freq, noise_freq, repeat - 25 * (version - 1));
                    trial_nr = trial_nr + 1;
                end
            end
        end
        %compute result without noise
        if model_nr == 1
            nPlans=floor(log(max(size(grating)-1)/4)/log(2)) + 1;
            output = CIWaM((grating + .5) .* .5, [5,4], nPlans, 1, 0, 2.967);
        elseif model_nr == 2
            for o = 1 : length(orientations)
                % loop over frequencies
                for f = 1 : length(stdev_pixels)
                    filter_response{o, f} = ourconv((grating + .5) .* .5, filters{o, f}, 0.5);  % pad image with gray
                end
            end
            output = flodog_normalize(filter_response, ...
                4, ... % normalization window size relative to filter being normed (n)
                1, ... % aspect ratio of window, 1 = round
                .5); % weighted sum across freqs (m)
            
        end
        
        value_inc = mean(output(idx_inc));
        value_dec = mean(output(idx_dec));
        fprintf(result, '%d none -1.0 0.5 %f %s 0.1 0.0 0\n', trial_nr, value_inc, grating_freq);
        trial_nr = trial_nr + 1;
        fprintf(result, '%d none 1.0 0.5 %f %s 0.1 0.0 0\n', trial_nr, value_dec, grating_freq);
        trial_nr = trial_nr + 1;
    end
    fclose(result);
    
end
end

function stimulus = prepare_grating(bar_width, n_bars, idx_check)
% create square wave grating
grating = ones(bar_width * n_bars) * .45;
index = [];
for i = 1:bar_width
    for j = 0: bar_width * 2: bar_width * (n_bars - 1)
        index = [index, i+j]; %#ok<AGROW>
    end
end
grating(index, :) = .55;
% place test squares at appropriate position
stimulus = ones(512) * .5;
tmp = size(grating) ./ 2;
tmp = tmp(1);
stimulus(257-tmp: 256+tmp, 257-tmp: 256+tmp) = grating;
stimulus(idx_check) = .5;
end

function stim_in_noise = add_noise(grating, noise_freq, rep, version)
noise_dir = ...
    '/Users/torsten/cogsci/PhD/whites_illusion/stim_variants/salmela/noise';
noise = load(sprintf('%s/noise512_31ppd_%1.2f_%d.mat', noise_dir, noise_freq, rep + 1));
noise = noise.noise;
% rotate noise mask 180deg on second half of repetitions
if version == 1
    noise = noise(end:-1:1, end:-1:1);
end
noise_masked = noise + .5;
stim_in_noise = .5 * (grating+noise_masked);
stim_in_noise = min(max(0, stim_in_noise), 1);
end

