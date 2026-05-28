function T = load_csv_table(csvPath)
% Load a simple comma-delimited CSV as a struct of columns.
fid = fopen(csvPath, 'r');
if fid < 0
    error('Could not open CSV file: %s', csvPath);
end
cleanup = onCleanup(@() fclose(fid));

header = fgetl(fid);
if ~ischar(header)
    error('CSV file is empty: %s', csvPath);
end
names = strsplit(strtrim(header), ',');
format = repmat('%s', 1, numel(names));
raw = textscan(fid, format, 'Delimiter', ',', 'ReturnOnError', false);

for idx = 1:numel(names)
    name = matlab.lang.makeValidName(strtrim(names{idx}));
    values = strtrim(raw{idx});
    numericValues = str2double(values);
    lowerValues = lower(values);
    isBool = all(strcmp(lowerValues, 'true') | strcmp(lowerValues, 'false'));

    if ~isempty(values) && all(~isnan(numericValues))
        T.(name) = numericValues;
    elseif isBool
        T.(name) = strcmp(lowerValues, 'true');
    else
        T.(name) = values;
    end
end
end
