clear all
close all
disp('Debut 1D');


N = 1000;
x = linspace(-5,5,N);
Lx = x.^3+sqrt(abs(x));
f = sin(Lx)./Lx;
f(Lx==0)=1;


plot(x,f);

figure; hold on;
d = getDispersion(x,f)
d = getDispersion(Lx,f)
