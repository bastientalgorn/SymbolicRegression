close all
clear all
disp('------ RS PostProcessing Categories -------');

global b0 y N count

N = 500;

% Generation de x, y et z
x = linspace(0,1,N);
dx = x(2)-x(1);
% y ref
y0 = getGaussianProcess(N);
% Boolean
s1 = rand/2;
s2 = 0.5+rand/2;
b0 = (s1 < y0) & (y0 < s2);
% Deuxième y

y = randn*getGaussianProcess(N)+randn*y0;
y = y-min(y);
y = y/max(y);
[ysort,ind] =sort(y);
b0sort = b0(ind);

figure;
hold on;
plot(x,y0,'b');
plot(x(b0),y0(b0),'.b');
plot([0 0;1 1],[1;1]*[s1 s2],'b');
plot(x,b0,'b.');
plot(x,y,'r');

 

% Find Best Interval (Filtrage des seuils)

listSeuils = [];
for i=1:N-1
    if b0sort(i)~=b0sort(i+1)
        listSeuils(end+1) = mean(ysort(i+[0 1]));
    end
end
listSeuils = [-inf listSeuils +inf];
NS = length(listSeuils);
emin = N;

for i1=1:NS-1
    s1 = listSeuils(i1);
    for i2=i1+1:NS
        s2 = listSeuils(i2);
        % Calcul de l'erreur
        b = (s1 < y) & (y < s2);
        e = sum(abs(b0-b));
        e = min(e,N-e);
        % Mémorisation
        if e <= emin
            emin = e;
            solution = [s1 s2];
        end
    end
end


disp('-------------------------------------------')
disp(['Nombre de valeurs de seuil : ' num2str(NS)]);
disp(['Erreur min: ' num2str(emin) ' / ' num2str(N)])
b = getBoolean(solution);
if getInv(solution);
    disp('Inversion');
    b = ~b;
end
disp(['Seuils : ' num2str(solution)]);


plot([0 0;1 1],[1;1]*solution,'r');
plot(x(b),y(b),'r.');
plot(x,-0.1+1.2*b,'r.');
        




