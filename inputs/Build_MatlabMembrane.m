close all
clear all

n = 7; % number of partitions in each dimension.
[X,Y] = meshgrid(linspace(0,1,2*n+1));
L = (40/51/0.9)*membrane(1,n);


DATA = [];

for i=1:2*n+1
    for j=1:2*n+1
        DATA(end+1,:) = [X(i,j) Y(i,j) L(i,j)];
    end
end
DATA