close all
clear all
disp('------ RS PostProcessing Categories -------');

global b0 y N count

N = 200;

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

 
% % Find Best Interval (Brut Force)
% emin = +inf;
% count = 0;
% ysort = unique(sort(y));
% NY = length(ysort);
% for i1=1:NY-1
%     if i1==1
%         y1 = -inf;
%     else
%         y1 = mean(ysort(i1+[0 1]));
%     end
%     for i2=i1+1:NY
%         if i2==NY
%             y2 = +inf;
%         else
%             y2 = mean(ysort(i2+[0 1]));
%         end
%         e = getError([y1 y2]);
%         if e <= emin
%             emin = e;
%             solution1 = [y1 y2];
%         end
%     end
% end
% 
% disp('-------------------------------------------')
% disp(['Erreur min: ' num2str(emin) ' / ' num2str(N)])
% b = getBoolean(solution1);
% if getInv(solution1);
%     disp('Inversion');
%     b = ~b;
% end
% disp(['Seuils (Brut Force) : ' num2str(solution1)]);
% disp(['Count : ' num2str(count)]);
% %subplot(2,2,2);hold on;
% plot([0 0;1 1],[1;1]*solution1,'r');
% plot(x(b),y(b),'r.');
% plot(x,-0.01+1.02*b,'r.');



% disp('-------------------------------------------')         
% count = 0;
% [solution2,emin] = fminsearch(@(x) getError(x),[1/4 3/4]); 
% disp(['Seuils (fminsearch) : ' num2str(solution2)]);
% disp(['Erreur min: ' num2str(emin) ' / ' num2str(N)])
% disp(['Count : ' num2str(count)]);


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
for i1=1:NS-1
    s1 = listSeuils(i1);
    for i2=i1+1:NS
        s2 = listSeuils(i2);
        e = getError([s1 s2]);
        if e <= emin
            emin = e;
            solution3 = [s1 s2];
        end
    end
end

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

yrbf = zeros(size(ysort));
for i=1:N
    dy = 0.25*(ysort(max(i-1,1))+ysort(min(i+1,N)));
    yrbf = yrbf+b0sort(i)*normpdf( (ysort-ysort(i))/dy ) /N;
end
yrbf = yrbf / max(abs(yrbf));
plot(ysort,yrbf,'r');
plot([1;1]*solution3,[0 0;1 1],'r');
plot(solution3,0.45*[1 1],'r');






% Cumul
listSeuilsPlot = listSeuils;
listSeuilsPlot([1 end]) = [0 1];
ratio = ones(1,NS);
iSup = NS;
iInf = 1;

% Build ratio
ratio(:) = 1;
for i=2:NS
    ratio(i) = getError(listSeuils([iInf i]))/N;
end

% Find Min
i = 1+find(diff(ratio(1:end-1)).*diff(ratio(2:end))<0);
%[emin,i] = min(ratio);
i = min(i);
% Attribution
eSup = getError(listSeuils([iInf i]));
eInf = getError(listSeuils([i iSup]));
if eSup<eInf
    iSup = i;
    disp('to Inf');
else
    iInf = i;
    disp('to Inf');
end

% Plot
plot(listSeuilsPlot,ratio,'g');
plot([1;1]*listSeuilsPlot([iInf iSup]),[0 0;1 1],'g');
plot(listSeuilsPlot([iInf iSup]),0.5*[1 1],'g');


disp(listSeuils([iInf iSup]))
disp(ratio);




% Build ratio
ratio(:) = 1;
for i=1:NS-1
    ratio(i) = getError(listSeuils([i iSup]))/N;
end

% Find Min
i = 1+find(diff(ratio(1:end-1)).*diff(ratio(2:end))<0);
%[emin,i] = min(ratio);
iSup = max(i);



% Plot
plot(listSeuilsPlot,ratio,'--g');
plot([1;1]*listSeuilsPlot([iInf iSup]),[0 0;1 1],'g');
plot(listSeuilsPlot([iInf iSup]),0.6*[1 1],'--g');

disp(listSeuils([iInf iSup]))
disp(ratio);











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