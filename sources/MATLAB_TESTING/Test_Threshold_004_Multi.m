close all
clear all
disp('------ RS PostProcessing Categories (Statistics) -------');


NEXP = 20;
if exist('tab.mat','file')
    load tab.mat
    disp(['LOAD : ' num2str(size(tab,1)) ' experiences']);
else
    tab = [];
    disp('INIT experience tab');
end

for nexp = 1:NEXP
    if mod(nexp,10)==0
        disp(nexp/NEXP)
    end
    N = 50+round(rand*1000);

    % Generation de x, y et z
    x = linspace(0,1,N);
    dx = x(2)-x(1);
    % y ref
    y0 = getGaussianProcess(N);
    % Boolean
    s1 = rand/2;
    s2 = 0.5+rand/2;
    b0 = (s1 < y0) & (y0 < s2);
    ntf = sum(b0);
    ntf = min(ntf,N-ntf);
    % Deuxième y

    y = randn*getGaussianProcess(N)+randn*y0;
    y = y-min(y);
    y = y/max(y);
    [ysort,ind] =sort(y);
    b0sort = b0(ind);

    % Find Best Interval (Filtrage des seuils)
    ind = find(b0sort(1:end-1)~=b0sort(2:end));
    listSeuils = (ysort(ind)+ysort(ind+1))/2;
    listSeuils = [-inf listSeuils +inf];
    NS = length(listSeuils);
    emin = N;

    for i1=1:NS-1
        s1 = listSeuils(i1);
        for i2=i1+1:NS
            % Calcul de l'erreur
            b = (s1 < y) & (y < listSeuils(i2));
            e = sum(abs(b0-b));
            e = min(e,N-e);
            e = min(e,emin);
        end
    end

    tab(end+1,:) = [N NS ntf e];
end


tab = [tab(:,1:2) min(tab(:,4),tab(:,1)-tab(:,4)) tab(:,3)];

disp(['Final experiences nb : ' num2str(size(tab,1))]);
save tab.mat tab
disp('Saving tab.mat file');

NEXP = size(tab,1);
N  = tab(:,1);
Nmin = min(N);
Nmax = max(N);
NS = tab(:,2);
ntf = tab(:,3);
e  = tab(:,4);


figure;
subplot(2,1,1); hold on;
% e/N  versur NS/N
% Coloration en fonction de ntrue
for k = 1:NEXP
    color = ntf(k)/N(k);
    color = [color 1-color 0];
    plot(e(k)/N(k),NS(k)/N(k),'.','color',color);
end
plot([0 0.5+0.5*i],':k');
xlabel('e/N');
ylabel('NS/N');
title('Red : ntf=0.5 // Green : ntf={0 or 1}');

subplot(2,1,2); hold on;
% e/N  versur NS/N
% Coloration en fonction de ntrue
for k = 1:NEXP
    color = ntf(k)/N(k);
    color = [color 1-color 0];
    plot(e(k)/N(k),NS(k)/e(k),'.','color',color);
end
plot([0 0.5],[2 1],'k');
xlabel('e/N');
ylabel('NS/e');
title('Red : ntf=0.5 // Green : ntf={0 or 1}');


figure
plot(e./N,NS./N,'.');



