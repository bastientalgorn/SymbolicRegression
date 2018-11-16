close all
clear all
disp('======== Build files for model construction/verification =======');

%file = 'Model_Volume2.txt'
%file = 'conductivity_reduced.csv'
%file = 'Martensite_Temperature.csv'
file = 'Molar_Volume.csv';

% READ ORIGINAL FILE
D = importdata(file);
[NP,NX] = size(D);

% BUILD THE INDEXES
bool = false(1,NP);
bool(1:round(NP*0.8)) = true;
bool = bool(randperm(NP));

% FILES NAMES
file_80 = strrep(file,'.','_80.');
file_20 = strrep(file,'.','_20.');

% BUILD THE FILES
fid_00 = fopen(file,'r');
fid_80 = fopen(file_80,'w');
fid_20 = fopen(file_20,'w');
for i = 1:NP
    line = fgets(fid_00);
    if bool(i)
        fwrite(fid_80,line);
    else
        fwrite(fid_20,line);
    end
end
fclose(fid_00);
fclose(fid_20);
fclose(fid_80);

% VERIFICATION OF THE FILES
D_20 = importdata(file_20);
D_80 = importdata(file_80);
if abs(sum(sum(D)) - sum(sum(D_20))-sum(sum(D_80)))>1e-6
    error('THE SUM OF THE FILES IS NOT CORRECT');
end

