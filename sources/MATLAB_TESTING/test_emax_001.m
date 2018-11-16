close all
clear all
disp('------ TEST SCALLING 2 ---------');

% F et H sont deux vecteurs. On souhaite trouver a et b qui minimise
% l'erreur max entre ces vecteurs (terme à terme)



f = sqrt(1:10);
a0 = randn;
b0 = randn;
disp([a0 b0]);
h = (f-b0)/a0+ randn(size(f));
%h = f + rand;


a = 10*randn;
b = (min(f-a*h)+max(f-a*h))/2;
E1 = max(abs(f-a*h-b))
E2 = (max(f-a*h)-min(f-a*h))/2

disp('=====================');
figure; hold on;

p = 1;
E = max(abs(f-a*h-b));

a = 1;
e = (max(f-a*h)-min(f-a*h))/2;
tabE = e;
tabA = a;
while p >1e-5
    if length(tabE) < 2
        d = f-a*h;
        [dmax,imax] = max(d);
        [dmin,imin] = min(d);
        de = -h(imax)+h(imin);
        anew = a-p*de;
    else
        N = length(tabE);
        [tabA,i] = sort(tabA);
        tabE = tabE(i);
        i = find(tabA==a);
        if i==1
            anew = 2*tabA(1)-tabA(2);
        elseif i==N
            anew = 2*tabA(N)-tabA(N-1);
        elseif i==2
            anew = (tabA(1)+tabA(2))/2;
        elseif i==N-1
            anew = (tabA(N)+tabA(N-1))/2;
        else
            anew = compute_a(tabA,tabE,i);
        end
    end
    d = f-anew*h;
    enew = (max(d)-min(d))/2;
    tabA(end+1) = anew;
    tabE(end+1) = enew;
    if enew < e
        a = anew;
        e = enew;
    else
        p = 0.5 * p;
    end

    plot(anew,enew,'r.')
end




disp('Finis');
disp(N)
plot(a,e,'ro')

va = linspace(min(tabA),max(tabA),1000);
vE = zeros(size(va));
for i = 1:length(va)
    a = va(i);
    b = (min(f-a*h)+max(f-a*h))/2;
    vE(i) = max(abs(f-a*h-b));
end


plot(va,vE);


% a = 1;
% a_old = -inf;
% while abs(a_old-a)>1e-8
%     d = f-a*h;
%     [dmax,imax] = max(d);
%     [dmin,imin] = min(d);
%     a_old = a;
%     a_target = (f(imax)+f(imin))/(h(imax)+h(imin));
%     a = 0.9*a+0.1*a_target;
%     disp(a)
% end
% 
% d = f-a*h;
% b = 0.5*(max(d)+min(d));
% disp([a b]);
% 
% figure; hold on;
% plot(f,'g');
% plot(a*h+b,':r');