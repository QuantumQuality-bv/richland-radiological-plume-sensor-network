function save_project_figure(fig, figureDir, basename)
% Save a figure from MATLAB or Octave using the best available export path.
pngPath = fullfile(figureDir, [basename '.png']);
pdfPath = fullfile(figureDir, [basename '.pdf']);

if exist('exportgraphics', 'file') == 2
    exportgraphics(fig, pngPath, 'Resolution', 300);
    exportgraphics(fig, pdfPath, 'ContentType', 'vector');
else
    print(fig, pngPath, '-dpng', '-r300');
    print(fig, pdfPath, '-dpdf');
end
end
