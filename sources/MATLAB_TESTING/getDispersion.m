function d = getDispersion(n,f)

[f,i] = sort(f);
n = n(i);

[n,i] = sort(n);
f = f(i);
n = n-n(1);
n = n/n(end);

plot(n,f,'color',rand(3,1));

d = sum(abs(diff(f)));