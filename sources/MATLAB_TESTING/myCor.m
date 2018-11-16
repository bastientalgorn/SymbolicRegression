function Q = myCor(x,fx,methode)

N = length(x);
%x =  x/std(x);
%fx = fx/std(fx);

% mean(abs(diff(fx)))
% mean(abs(diff(x)))



switch methode
    case 1
        Q = abs(corr(x(:),fx(:)));   
       
    case 2
        % Pas de tri
        Dx  = abs(diff(x(:)));
        Dfx = abs(diff(fx(:)));
        %p = Dfx./Dx;
        %Q = 1/std(p);
        Q = corr(Dx,Dfx);

    case 3
        % Comparaison de toutes les paires
        % Matrice de distance
        Dx = zeros(N*(N-1)/2,1);
        Dfx = Dx;
        k = 1;
        for i=1:N-1
            for j=i+1:N
                Dx(k)  = x(i) -x(j);
                Dfx(k) = fx(i)-fx(j);
                k = k + 1;
            end
        end
        Q = corr(abs(Dx),abs(Dfx));
        
    case 4
        % Comparaison de toutes les paires
        % Matrice de distance
        Dx = zeros(N*(N-1)/2,1);
        Dfx = Dx;
        k = 1;
        for i=1:N-1
            for j=i+1:N
                Dx(k)  = x(i) -x(j);
                Dfx(k) = fx(i)-fx(j);
                k = k + 1;
            end
        end
        Dx =  Dx/std(Dx);
        Dfx =  Dfx/std(Dfx);
        Dx = abs(Dx);
        Dfx = abs(Dfx);
        Q = 1-max(Dfx.*exp(-10*Dx));
        
        
    case 5
        % Comparaison de toutes les paires
        % Matrice de distance
        Dx  = diff(x(:));
        Dfx = diff(fx(:));
        Dx =  Dx/std(Dx);
        Dfx =  Dfx/std(Dfx);
        Dx = abs(Dx);
        Dfx = abs(Dfx);
        Q = 1-mean(Dfx.*exp(-3*Dx));
        
    case 6
        % Comparaison de toutes les paires
        % Matrice de distance
        Dx  = diff(x(:));
        Dfx = diff(fx(:));
        Dx =  Dx/std(Dx);
        Dfx =  Dfx/std(Dfx);
        Dx = abs(Dx);
        Dfx = abs(Dfx);
        Q = 1-mean((Dfx).*exp(-10*Dx));
        
        
        
        
        
        
    otherwise
        display(methode)
        error('No valid method');
        
end
%Q = 1/Q;
            