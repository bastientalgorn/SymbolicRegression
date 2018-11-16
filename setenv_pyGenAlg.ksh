#!bin/ksh

PYGENALG_DIR=/home/bastien/SYMBOLIC/Code_v009_LinkNode/pyGenAlg
PATH_TO_ADD=$PYGENALG_DIR/sources/
if ! echo $PYTHONPATH | grep $PATH_TO_ADD > /dev/null
then
  export PYTHONPATH=$PATH_TO_ADD:$PYTHONPATH
fi

PYPARAMMANAGER_DIR=/home/bastien/SYMBOLIC/pyParamManager
PATH_TO_ADD=$PYPARAMMANAGER_DIR/sources/
if ! echo $PYTHONPATH | grep $PATH_TO_ADD > /dev/null
then
  export PYTHONPATH=$PATH_TO_ADD:$PYTHONPATH
fi

SYMBOLICREGRESSION_DIR=/home/bastien/SYMBOLIC/Code_v009_LinkNode/SymbolicRegression
PATH_TO_ADD=$SYMBOLICREGRESSION_DIR/sources/
if ! echo $PYTHONPATH | grep $PATH_TO_ADD > /dev/null
then
  export PYTHONPATH=$PATH_TO_ADD:$PYTHONPATH
fi
