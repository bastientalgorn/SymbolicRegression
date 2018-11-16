close all
clear all
disp('======== ANALYSE BIG RUN RegSym ============');


listModelShort = {'memb','dav1','sinc','cole','quin','sext'};
listParamShort = {'bas','spe','ful'};

directory='/tmp/RUN_RegSym';
prefix='run_';


for model = listModelShort
    model = model{1};
    figure('name',model)
    hold on;
    for param = listParamShort
        param = param{1};
        listRun = dir([directory '/' prefix model '_' param '*']);
        listRun = {listRun(:).name};
        convTab = [];
        switch param
            case 'bas'
                color='r';
            case 'spe'
                color='g';
            case 'ful'
                color='b';
        end
        for k=1:length(listRun)
             conv = readConvergenceFile([directory '/' listRun{k} '/convergence.txt']);
             convTab(:,k) = conv;
             %plot((1:genNb),conv,color);
        end
        genNb = size(convTab,1);
        p=plot((1:genNb),mean(convTab,2),color,'linewidth',2);
        set(get(p,'parent'),'yscale','log');
    end
end