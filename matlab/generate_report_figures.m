% Generate final report figures from MATLAB-ready CSV exports.
% Run from the repository root after scripts/08_export_matlab_inputs.py.

rootDir = fileparts(fileparts(mfilename('fullpath')));
exportDir = fullfile(rootDir, 'data', 'processed', 'matlab_exports');
figureDir = fullfile(rootDir, 'figures');
if ~exist(figureDir, 'dir'), mkdir(figureDir); end

saveBoth = @(fig, name) save_report_figure(fig, figureDir, name);

plume = readtable(fullfile(exportDir, 'plume_grid.csv'));
viewRows = plume.x_m >= 0 & plume.x_m <= 2500 & plume.y_m >= -500 & plume.y_m <= 500 & plume.concentration_bq_m3 > 0;
fig = figure('Color', 'w', 'Position', [100, 100, 760, 440]);
scatter(plume.x_m(viewRows), plume.y_m(viewRows), 22, log10(plume.concentration_bq_m3(viewRows)), 'filled');
hold on;
plot(0, 0, 'rp', 'MarkerFaceColor', 'r', 'MarkerSize', 12);
quiver(150, 420, 500, 0, 0, 'k', 'LineWidth', 1.5, 'MaxHeadSize', 0.5);
text(670, 420, 'wind direction', 'FontSize', 9);
cb = colorbar;
cb.Label.String = 'log10 C (Bq m^{-3})';
xlabel('Downwind distance x (m)');
ylabel('Crosswind distance y (m)');
title('Synthetic Gaussian Plume, Log-Scaled Concentration');
xlim([0 2500]);
ylim([-500 500]);
grid on;
saveBoth(fig, 'plume_log_contour');

centerline = readtable(fullfile(exportDir, 'centerline_profile.csv'));
fig = figure('Color', 'w', 'Position', [100, 100, 640, 420]);
semilogy(centerline.x_downwind_m, centerline.concentration_bq_m3, 'LineWidth', 2);
xlabel('Downwind distance x (m)');
ylabel('C (Bq m^{-3})');
title('Centerline Concentration Profile');
grid on;
saveBoth(fig, 'centerline_profile');

crosswind = readtable(fullfile(exportDir, 'crosswind_profile.csv'));
fig = figure('Color', 'w', 'Position', [100, 100, 640, 420]);
plot(crosswind.y_crosswind_m, crosswind.concentration_bq_m3, 'LineWidth', 2);
xline(0, '--k', 'Centerline');
xline(200, ':k', 'R002 offset');
xlabel('Crosswind distance y (m)');
ylabel('C (Bq m^{-3})');
title('Crosswind Concentration Profile at x = 1000 m');
grid on;
saveBoth(fig, 'crosswind_profile');

network = readtable(fullfile(exportDir, 'network_metrics.csv'));
fig = figure('Color', 'w', 'Position', [100, 100, 760, 440]);
metricMatrix = [network.score, network.P_detect, network.C_cost ./ max(network.C_cost), network.W_coverage];
bar(categorical(network.network_id), metricMatrix);
ylabel('Normalized metric value');
title('Network Metric Comparison');
legend({'Score', 'P detect', 'Cost proxy normalized', 'Wind-sector coverage'}, 'Location', 'northoutside', 'NumColumns', 2);
grid on;
saveBoth(fig, 'network_metrics');

likelihood = readtable(fullfile(exportDir, 'noisy_likelihood_grid.csv'));
estimate = readtable(fullfile(exportDir, 'noisy_source_estimate.csv'));
err = readtable(fullfile(exportDir, 'noisy_loc_error_summary.csv'));
fig = figure('Color', 'w', 'Position', [100, 100, 620, 520]);
deltaJ = likelihood.J - min(likelihood.J);
scatter(likelihood.x_m, likelihood.y_m, 28, deltaJ, 'filled');
hold on;
plot(err.true_x_m(1), err.true_y_m(1), 'gp', 'MarkerFaceColor', 'g', 'MarkerSize', 14);
plot(estimate.estimated_x_m(1), estimate.estimated_y_m(1), 'rx', 'LineWidth', 2, 'MarkerSize', 10);
axis equal;
colorbar;
xlabel('Candidate x (m)');
ylabel('Candidate y (m)');
title('Noisy Synthetic Source Reconstruction Surface');
legend({'Delta J grid', 'True source', 'Estimated source'}, 'Location', 'best');
grid on;
saveBoth(fig, 'src_recon_likelihood');

sensitivity = readtable(fullfile(exportDir, 'sensitivity_tornado.csv'));
[~, order] = sort(abs(sensitivity.concentration_pct_change), 'ascend');
fig = figure('Color', 'w', 'Position', [100, 100, 720, 500]);
barh(categorical(sensitivity.case_id(order)), sensitivity.concentration_pct_change(order));
xline(0, 'k');
xlabel('Concentration change (%)');
title('One-at-a-Time Sensitivity Tornado');
grid on;
saveBoth(fig, 'sensitivity_tornado');

mc = readtable(fullfile(exportDir, 'monte_carlo_results_final.csv'));
fig = figure('Color', 'w', 'Position', [100, 100, 960, 360]);
tiledlayout(1, 3);
nexttile; histogram(mc.concentration_Bq_m3, 35); xlabel('C (Bq m^{-3})'); ylabel('Count'); title('Concentration');
nexttile; histogram(mc.time_to_detection_s, 35); xlabel('Time to threshold crossing (s)'); ylabel('Count'); title('Time to threshold');
nexttile; histogram(mc.localization_error_m, 35); xlabel('Localization error (m)'); ylabel('Count'); title('Localization error');
saveBoth(fig, 'mc_uncertainty_summary');

function save_report_figure(fig, figureDir, name)
    exportgraphics(fig, fullfile(figureDir, [name '.pdf']), 'ContentType', 'vector');
    exportgraphics(fig, fullfile(figureDir, [name '.png']), 'Resolution', 300);
end
