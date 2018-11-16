close all
clear all
disp('------------ RS PostProcessing Categories ----------------');

N = 200;
K = 3;

listCat = (0:K-1);


% Generation de x, y et z
x = linspace(-3,+3,N);
z = int8(zeros(size(x)));
y0 = getGaussianProcess(N);


%seuilsCat = sort([0,rand(1,K-1),1]);
seuilsCat = linspace(0,1,K+1);
for k = 1:K
    s1 = seuilsCat(k);
    s2 = seuilsCat(k+1);
    z( (s1<=y0) & (y0<=s2) ) = listCat(k);
end

figure;
hold on;
plot(x,1+K*y0,'k');
plot(x,z,'k*');
clear seuilsCat y0 s1 s2 


y = getGaussianProcess(N);

for k = 1:K
    c = (k-1)/(K-1)*[-1 1 0] + [1 0 0];
    i= find(z==listCat(k));
    ind{k} = i;
    plot(x(i),1+K*y(i),'*','color',c);
    m(k) = mean(y(i));
    plot([x(1) x(end)],K*m(k)*[1 1],'color',c);
    v(k) = std(y(i));
end

[msort,ordre] = sort(m);
vsort = v(ordre);

disp('Calcul seuils');
msort
for k=1:K-1
    k
    s1 = msort(k);
    d = msort(k+1)-s1;
    r = vsort(k)/(vsort(k)+vsort(k+1));
    seuil(k) = s1+d*r
    plot([x(1) x(end)],K*seuil(k)*[1 1],'k--');
end