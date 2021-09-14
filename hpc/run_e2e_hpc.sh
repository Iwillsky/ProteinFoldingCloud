#!/bin/bash

# make the script stop when error (non-true exit code) is occured
set -e

############################################################
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('conda' 'shell.bash' 'hook' 2> /dev/null)"
eval "$__conda_setup"
unset __conda_setup
# <<< conda initialize <<<
############################################################

SCRIPT=`realpath -s $0`
export PIPEDIR=`dirname $SCRIPT`

CPU="8"  # number of CPUs to use
MEM="64" # max memory (in GB)

# Inputs:
IN="$1"                # input.fasta
WDIR=`realpath -s $2`  # working folder
RosettaJobId="$3"
RPREFIX="rjob${RosettaJobId}"
DIR_LOG=$WDIR/log_${RosettaJobId}

if [ x$4 != x ]
then
    CPU="$4"  # set cpu if param exists
fi
if [ x$5 != x ]
then
    MEM="$5"  # set memory if param exists
fi

LEN=`tail -n1 $IN | wc -m`

mkdir -p $DIR_LOG

conda activate RoseTTAFold
############################################################
# 1. generate MSAs
############################################################
if [ ! -s $WDIR/$RPREFIX.msa0.a3m ]
then
    echo "Running HHblits of JobId ${RPREFIX}"
    $PIPEDIR/input_prep/make_msa.sh $IN $WDIR $CPU $MEM $RPREFIX > $DIR_LOG/make_msa.stdout 2> $DIR_LOG/make_msa.stderr
fi


############################################################
# 2. predict secondary structure for HHsearch run
############################################################
if [ ! -s $WDIR/$RPREFIX.ss2 ]
then
    echo "Running PSIPRED of JobId ${RPREFIX}"
    $PIPEDIR/input_prep/make_ss.sh $WDIR/$RPREFIX.msa0.a3m $WDIR/$RPREFIX.ss2 > $DIR_LOG/make_ss.stdout 2> $DIR_LOG/make_ss.stderr
fi


############################################################
# 3. search for templates
############################################################
DB="$WDIR/pdb100_2021Mar03/pdb100_2021Mar03"  # modify DIR as WDIR
if [ ! -s $WDIR/$RPREFIX.hhr ]
then
    echo "Running hhsearch of JobId ${RPREFIX}"
    HH="hhsearch -b 50 -B 500 -z 50 -Z 500 -mact 0.05 -cpu $CPU -maxmem $MEM -aliw 100000 -e 100 -p 5.0 -d $DB"
    cat $WDIR/$RPREFIX.ss2 $WDIR/$RPREFIX.msa0.a3m > $WDIR/$RPREFIX.msa0.ss2.a3m
    $HH -i $WDIR/$RPREFIX.msa0.ss2.a3m -o $WDIR/$RPREFIX.hhr -atab $WDIR/$RPREFIX.atab -v 0 > $DIR_LOG/hhsearch.stdout 2> $DIR_LOG/hhsearch.stderr
fi


############################################################
# 4. end-to-end prediction
############################################################
if [ ! -s $WDIR/$RPREFIX.3track.npz ]
then
    echo "Running end-to-end prediction of JobId ${RPREFIX}"
    # modify DIR as WDIR of weights
    python $PIPEDIR/network/predict_e2e.py \
        -m $WDIR/weights \
        -i $WDIR/$RPREFIX.msa0.a3m \
        -o $WDIR/$RPREFIX.e2e \
        --hhr $WDIR/$RPREFIX.hhr \
        --atab $WDIR/$RPREFIX.atab \
        --db $DB 1> $DIR_LOG/network.stdout 2> $DIR_LOG/network.stderr
fi
echo "Done"
