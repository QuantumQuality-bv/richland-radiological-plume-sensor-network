function plot_detector_network()
% Plot candidate detector locations and deterministic network membership.
rootDir = fileparts(fileparts(mfilename('fullpath')));
exportDir = fullfile(rootDir, 'data', 'processed', 'matlab_exports');
figureDir = fullfile(rootDir, 'figures', 'matlab');
if ~exist(figureDir, 'dir'), mkdir(figureDir); end

T = load_csv_table(fullfile(exportDir, 'candidate_detector_map.csv'));
fig = figure('Color', 'w');
hold on;
scatter(T.x_m, T.y_m, 36, [0.45 0.45 0.45], 'filled', 'DisplayName', 'Candidate');
if isfield(T, 'in_N3')
    selected = logical(T.in_N3);
    scatter(T.x_m(selected), T.y_m(selected), 80, [0.0 0.35 0.70], 'filled', 'DisplayName', 'N3 selected');
end
plot(0, 0, 'kp', 'MarkerSize', 12, 'MarkerFaceColor', 'y', 'DisplayName', 'Synthetic source');
xlabel('x (m)');
ylabel('y (m)');
title('Synthetic Detector Network Map');
legend('Location', 'best');
grid on;
axis equal;
save_project_figure(fig, figureDir, 'detector_network');
end
