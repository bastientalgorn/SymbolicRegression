close alll
clear al
NomFichier = 'MembraneMatlab.txt';
fid = fopen(NomFichier,'w');

L = membrane(1);
[NX,NY] = size(L);
for nx = 1:NX
    for ny = 1:NY
        fwrite(fid,num2str([nx ny L(nx,ny)],5));
        fwrite(fid,char(10));
    end
end

fclose(fid)

edit(NomFichier)