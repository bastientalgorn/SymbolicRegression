close all
clear all
disp('------------------ test correlation ---------------');

NEXP = 1000;
N = 1000;

methode = 3;
biais = 0.0;
Ssum = 0;
Nq = 0;

for nexp = 1:NEXP

    x = 5*randn(N,1);
    y = 5*randn(N,1);
    x = round(x);
    y = round(y);
    r = sqrt(x.^2+y.^2);
    f = sin(2*pi*r);

    z = rand(N,1);
    zz = rand(N,1);
    
    cor_ff = myCor(f,f,methode,biais);
    cor_xf = myCor(x,f,methode,biais);
    cor_rf = myCor(r,f,methode,biais);
    cor_zz = myCor(z,zz,methode,biais);

    Nq = Nq + (cor_ff < 1-1e-6);
    S = min(cor_xf,cor_zz)/cor_rf;
    Ssum = Ssum + S/NEXP;
end

display(Ssum);
if Nq
    disp('-----------------------');
    disp(Nq);
    disp('-----------------------');
end


% 
% tabQ = 2.^(0:5);
% 
% for k = 1:length(tabQ)
%     Q = tabQ(k)
%     arg = [0 Q];
%  	mfr(k) = myCor(r,f,arg); 
%     mzz(k) = myCor(z,zz,arg);
% end
% figure; 
% hold on;
% plot(tabQ,mfr,'g');
% plot(tabQ,mzz,'r');
