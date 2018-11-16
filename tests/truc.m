function f = truc(varargin)

% FileName = truc.m
% DataFile = Sextic
% NodesNumber = 11
% UsedVariables = [0 7 9]    ( 3 out of 10 )

%% Inputs Management
NX = 10;
if nargin==1
    if size(varargin{1},2)~=NX
        error(['The input argument must have ' num2str(NX) ' columns.']);
    end
    for i=1:NX
        eval(['x' num2str(i-1) ' = varargin{1}(:,' num2str(i) ');']);
    end
else
    if nargin~=NX
        error(['The function must have ' num2str(NX) ' arguments.']);
    end
    for i=1:NX
        eval(['x' num2str(i-1) ' = varargin{' num2str(i) '};']);
    end
end

%% Algorithm
