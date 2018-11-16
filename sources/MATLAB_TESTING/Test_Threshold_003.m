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

y = 111*getGaussianProcess(N)+0.9*y0;
y = y-min(y);
y = y/max(y);
[ysort,ind] =sort(y);
b0sort = b0(ind);

figure;
subplot(2,1,1);
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
emin = +inf;
count = 0;
tab = zeros(NS,NS);
for i1=1:NS-1
    s1 = listSeuils(i1);
    for i2=i1+1:NS
        s2 = listSeuils(i2);
        e = getError([s1 s2]);
        tab(i1,i2) = e;
        if e <= emin
            emin = e;
            solution3 = [s1 s2];
        end
    end
end
tab = tab+tab';

disp('-------------------------------------------')
disp(['Nombre de valeurs de seuil : ' num2str(NS)]);
disp(['Erreur min: ' num2str(emin) ' / ' num2str(N)])
b = getBoolean(solution3);
if getInv(solution3);
    disp('Inversion');
    b = ~b;
end
disp(['Seuils (Solution 3) : ' num2str(solution3)]);
disp(['Count : ' num2str(count)]);

plot([0 0;1 1],[1;1]*solution3,'r');
plot(x(b),y(b),'r.');
plot(x,-0.1+1.2*b,'r.');
        



% Densité
subplot(2,1,2);
hold on;
plot(ysort,b0sort,'.');

plot([1;1]*solution3,[0 0;1 1],'r');
plot(solution3,0.5*[1 1],'r');







% Cumul
listSeuilsPlot = listSeuils;
listSeuilsPlot([1 end]) = [0 1];
ratio = ones(1,NS);
iSup = NS;
iInf = 1;

go = +1;
for k=1:4
    
    % Build ratio
    ratio(:) = 1;
    if go == +1
        for i=iInf+1:NS
            ratio(i) = getError(listSeuils([iInf i]))/N;
        end
    elseif go == -1
        for i=1:iSup-1
            ratio(i) = getError(listSeuils([i iSup]))/N;
        end
    end
        
    % Find Min
    i = 1+find(diff(ratio(1:end-1)).*diff(ratio(2:end))<0);
    %[emin,i] = min(ratio);
    if go == +1
        i = min(i);
    elseif go == -1
        i = max(i);
    end
    
    % Attribution
    eSup = getError(listSeuils([iInf i]));
    eInf = getError(listSeuils([i iSup]));
    if eSup<eInf
        iSup = i;
        disp([num2str(eSup) ' to Sup']);
        go = -1;
    else
        iInf = i;
        disp([num2str(eInf) ' to Inf']);
        go = +1;
    end

    % Plot
    plot(listSeuilsPlot,ratio,'g');
    plot([1;1]*listSeuilsPlot([iInf iSup]),[0 0;1 1],'g');
    plot(listSeuilsPlot([iInf iSup]),0.05+k*0.05+[0 0],'g');


    disp(listSeuils([iInf iSup]))

end







% % Attribution
% eInf = getError(listSeuils([iInf i]));
% eSup = getError(listSeuils([i iSup]));
% if eSup>eInf
%     iSup = i;
%     disp('to Inf');
% else
%     iInf = i;
%     disp('to Inf');
% end