close all
clear all
disp('------ RS Special Correlation -------');

N = 50; % Nb de points
NEXP = 500;

methodList = [1  5 6];
methodMax = max(methodList);


tabC = zeros(NEXP,methodMax);

for e = 1:NEXP
    % signaux
    y1 = randn*getGaussianProcess(N);
    y2 = randn*getGaussianProcess(N)+randn*y1;
    
    for method = 1:methodMax
        tabC(e,method) = myCor(y1,y2,method);
    end
end





for method = methodList
    v = tabC(:,method);
    v = v-min(v);
    v = v/max(v);
    tabC(:,method) = v;
end


% [~,i] = sort(tabC(:,1));
% tabC = tabC(i,:);
% 
% figure;hold on;
% for method = methodList
%     [~,i] = sort(tabC(:,method));
%     plot(i,'.','color',method/methodMax*[1 -1 0]+[0 1 0]);
% end


figure;
listColor = 'gbrkcmy';

subplot(2,1,1);hold on;
k = 1;
for method = methodList
    plot(tabC(:,1),tabC(:,method),['.',listColor(k)]);
    k = k+1;
end
xlabel('valeur');

subplot(2,1,2);hold on;
[~,i] = sort(tabC(:,1));
tabC = tabC(i,:);
k = 1;
for method = methodList
    [~,i] = sort(tabC(:,method));
    plot(i,['.',listColor(k)]);
    k = k+1;
end
xlabel('ordre');
