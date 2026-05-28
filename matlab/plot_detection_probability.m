function plot_detection_probability()
% Plot synthetic Monte Carlo threshold-crossing probability.
rootDir = fileparts(fileparts(mfilename('fullpath')));
exportDir = fullfile(rootDir, 'data', 'processed', 'matlab_exports');
figureDir = fullfile(rootDir, 'figures', 'matlab');
if ~exist(figureDir, 'dir'), mkdir(figureDir); end

T = load_csv_table(fullfile(exportDir, 'detect_prob_summary.csv'));
fig = figure('Color', 'w');
x = 1:numel(T.detection_probability);
bar(x, T.detection_probability);
set(gca, 'XTick', x, 'XTickLabel', T.run_name);
ylabel('threshold-crossing probability');
xlabel('Monte Carlo run');
title('Synthetic Detection Probability');
ylim([0 1]);
grid on;
save_project_figure(fig, figureDir, 'detection_probability');
end
