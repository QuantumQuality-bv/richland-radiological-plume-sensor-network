function plot_plume_contours()
% Plot synthetic Gaussian plume concentration contours from exported CSV data.
rootDir = fileparts(fileparts(mfilename('fullpath')));
exportDir = fullfile(rootDir, 'data', 'processed', 'matlab_exports');
figureDir = fullfile(rootDir, 'figures', 'matlab');
if ~exist(figureDir, 'dir'), mkdir(figureDir); end

T = load_csv_table(fullfile(exportDir, 'plume_grid.csv'));
x = unique(T.x_m);
y = unique(T.y_m);
[X, Y] = meshgrid(x, y);
Z = griddata(T.x_m, T.y_m, T.concentration_Bq_m3, X, Y);

fig = figure('Color', 'w');
contourf(X, Y, Z, 20, 'LineColor', 'none');
colorbar;
xlabel('x (m)');
ylabel('y (m)');
title('Synthetic Gaussian Plume Concentration (Bq/m^3)');
axis equal tight;
save_project_figure(fig, figureDir, 'plume_contour');
end
