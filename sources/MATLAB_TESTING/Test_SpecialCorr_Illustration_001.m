close all
clear all
disp('------ RS Special Correlation -------');

N = 1000; % Nb de points
x = 2*rand(N,1)-1;
y = 2*rand(N,1)-1;


figure;
v = 'f = sin(2*pi*x);'
eval(v)
c1 = myCor(x,f,1);
c2 = myCor(x,f,2);
plot(x,f,'.');
xlabel([v ' ' num2str(c1) ' ' num2str(c2)]);


figure;
v = 'f = x+y;'
eval(v)
c1 = myCor(x,f,1);
c2 = myCor(x,f,2);
plot(x,f,'.');
xlabel([v ' ' num2str(c1) ' ' num2str(c2)]);



figure;
v = 'f = x+y;'
eval(v)
c1 = myCor(x,f,1);
c2 = myCor(x,f,2);
plot(x,f,'.');
xlabel([v ' ' num2str(c1) ' ' num2str(c2)]);
