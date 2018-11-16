close all
clear all
NomFichier = 'SinusCardinal2D.txt';
fid = fopen(NomFichier,'w');


N = 20;
xmax = 3;
x = linspace(-1,3,N);
L = zeros(N,N);
for nx = 1:N
    for ny = 1:N
        r = norm([x(nx),x(ny)]);
        f = sinc(r);
        L(nx,ny) = f;
        fwrite(fid,num2str([x(nx),x(ny),f],5));
        fwrite(fid,char(10));
    end
end

fclose(fid)
imagesc(L)
edit(NomFichier)