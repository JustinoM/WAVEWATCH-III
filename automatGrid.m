% Justino justino@icm.csic.es
% WW3 tools
% Provide the name of the gridgen namelist file and the folder where reference, namelist ... folders is located 
% (typically TUTORIAL_GRIDGEN)
% The gridgen namelist name must be located in namelist folder
% output files are stored in data_dir
%
% execute as 
% matlab  -nodisplay -nodesktop -nosplash -nojvm -r "try, automatGrid;  catch, disp('failed execution'), end, quit"

data_nml='gridgen.MED-0125_gebco.nml';
BASE='/data/lustre/WW3/TUTORIAL_GRIDGEN/';

ref_dir = [BASE,'reference'];
nml_dir = [BASE,'namelist'];
data_dir= [BASE,'data'];
bin_dir = [BASE,'bin'];
addpath(bin_dir,'-END');
cd(nml_dir)
create_grid(data_nml)

