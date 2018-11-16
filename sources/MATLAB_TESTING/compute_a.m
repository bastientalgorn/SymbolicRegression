function a = compute_a(tabA,tabE,i)

u = tabA(i-2);
v = tabA(i-1);
x = tabA(i+1);
y = tabA(i+2);

fu = tabE(i-2);
fv = tabE(i-1);
gx = tabE(i+1);
gy = tabE(i+2);

df = (fu-fv)/(u-v);
f0 = fv-v*df;
dg = (gx-gy)/(x-y);
g0 = gx-x*df;

disp('in compute_a');
disp(tabA(i-2,i+2))
disp(tabE(i-2,i+2))
if df*dg<0
    a = - (g0-f0)/(dg-df);
    a = max(a,2*u-v);
    a = min(a,2*y-x);
    disp('df*dg<0');
else
    if df>0
        a = 2*u-v;
        disp('df<0');
    else
        a = 2*y-x;
        disp('df>0');
    end
end
disp(a)




