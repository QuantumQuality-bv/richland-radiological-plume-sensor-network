function plot_source_reconstruction()
% Plot synthetic source reconstruction likelihood surface.
rootDir = fileparts(fileparts(mfilename('fullpath')));
exportDir = fullfile(rootDir, 'data', 'processed', 'matlab_exports');
figureDir = fullfile(rootDir, 'figures', 'matlab');
if ~exist(figureDir, 'dir'), mkdir(figureDir); end

L = load_csv_table(fullfile(exportDir, 'likelihood_grid.csv'));
E = load_csv_table(fullfile(exportDir, 'source_estimate.csv'));
x = unique(L.x_m);
y = unique(L.y_m);
[X, Y] = meshgrid(x, y);
Z = griddata(L.x_m, L.y_m, L.normalized_likelihood, X, Y);

fig = figure('Color', 'w');
contourf(X, Y, Z, 20, 'LineColor', 'none');
hold on;
plot(E.estimated_x_m, E.estimated_y_m, 'kp', 'MarkerSize', 12, 'MarkerFaceColor', 'y', 'DisplayName', 'Estimate');
colorbar;
xlabel('candidate x (m)');
ylabel('candidate y (m)');
title('Synthetic Source Reconstruction Likelihood');
legend('Location', 'best');
axis equal tight;
save_project_figure(fig, figureDir, 'source_reconstruction');
end
