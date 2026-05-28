function plot_sensitivity_surfaces()
% Plot synthetic one-at-a-time sensitivity ranking.
rootDir = fileparts(fileparts(mfilename('fullpath')));
exportDir = fullfile(rootDir, 'data', 'processed', 'matlab_exports');
figureDir = fullfile(rootDir, 'figures', 'matlab');
if ~exist(figureDir, 'dir'), mkdir(figureDir); end

T = load_csv_table(fullfile(exportDir, 'sensitivity_tornado.csv'));
topN = min(10, numel(T.case_id));
fig = figure('Color', 'w');
barh(1:topN, T.concentration_pct_change(1:topN));
set(gca, 'YTick', 1:topN, 'YTickLabel', T.case_id(1:topN));
xlabel('concentration change (%)');
ylabel('sensitivity case');
title('Synthetic Sensitivity Tornado');
grid on;
save_project_figure(fig, figureDir, 'sensitivity_tornado');
end
