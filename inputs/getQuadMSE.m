DATA = importdata('CONDUCTIVITY2.csv');
X = DATA(:,1:end-1);
F = DATA(:,end);

[NP,NX] = size(X);

MAT = zeros(NP, (NX+1)*(NX+2)/2);
k = 0;
for i=1:NX+1
    if i<=NX
        xi = X(:,i);
    else
        xi = ones(NP,1);
    end
       
    for j=1:i
        k = k+1;
        if j<=NX
            xj = X(:,j);
        else
            xj = ones(NP,1);
        end
        MAT(:,k) = xi.*xj;
    end
end


c = MAT\F;
F2 = MAT*c;
MSE = mean((F-F2).^2)