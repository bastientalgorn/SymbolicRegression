function f = getGaussianProcess(N1)

N = N1*2;

module = abs((1:N)-(N+1)/2);
module = max(0,module-N*0.45);
f = module .* exp(2*1i*rand(1,N));
%f = fftshift(f);
f = real(ifft(f));

f = f(round(N1/2)+(1:N1));
f = f-min(f);
f = f/max(f);