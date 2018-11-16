close all
clear all
disp('DEBUT');


N = 500;
x = 10-20*rand(N,1);
y = 10-20*rand(N,1);
z = 10-20*rand(N,1);

r = sqrt(x.^2+y.^2);
f = sin(r)./r+z;
plot3(x,y,f,'.');

figure;hold on;
d = getDispersion(r.^2,f)
d = getDispersion(x+y,f)
d = getDispersion(rand(N,1),f)
