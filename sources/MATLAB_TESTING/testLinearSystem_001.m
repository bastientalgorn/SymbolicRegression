close all
clear all
disp('--------- TEST LINEAR SYSTEM ------------------');

Nc = 5;
Nx = 50;


y0 = getGaussianProcess(Nx);
b = y0(:);

A = zeros(Nx,Nc);
for i = 1:Nc
    if i == 1
        c = 0.01;
    else
        c = randn;
    end
    A(:,i) = y0+randn*getGaussianProcess(Nx);
end



c_old = zeros(Nc,1);
c = 0.5* ones(Nc,1);
E = +inf;
L0 = 1;
dc = zeros(Nc,1);
iter = 1;

figure; hold on;

while (L0>1e-6) && (iter<500)
    disp('-----------------------------')
    c_old = c;
    E_old = E;
    dc_old = dc;
    
    dc_new = A'*A*c - A'*b;
    dc = 0.5*(dc_new+dc_old);
    dc = dc_new;
    
    disp(['c : ' num2str(c')])
    disp(['dc: ' num2str(dc')])

    % Suppression des composantes de dc qui sont déjà saturées   
    dc((c==1)&(dc<0)) = 0;
    dc((c==0)&(dc>0)) = 0;
    
    % Calcul de la valeur max de L pour ne pas sortir du domaine admissible
    ipos = find(dc>0);
    ineg = find(dc<0); 
    Lpos = min(c(ipos)./dc(ipos));
    Lneg = min((c(ineg)-1)./dc(ineg));
    Lmin = norm(A'*A*dc)/norm(dc);
      
    L = min([L0 Lpos Lneg]);
    c = c-L*dc;
    E = norm(A*c-b);
    disp(['L : ' num2str(L)])

    disp(['E : ' num2str(E)])
    plot(iter,log(E),'.')
    plot(iter,log(L),'.g')
    drawnow
    
    if E>E_old
        plot(iter,log(E),'or');
        c = c_old;
        E = E_old;
        %dc_old = dc_new;
        L0 = 0.5*L0;
        
    else
        L0 = 1.1*L0;
    end
    iter = iter+1;
end

