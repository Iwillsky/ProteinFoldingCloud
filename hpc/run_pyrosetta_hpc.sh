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
DIR_PDB3TRACK=$WDIR/pdb-3track_${RosettaJobId}
DIR_MODEL=$WDIR/model_${RosettaJobId}
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
DB="$WDIR/pdb100_2021Mar03/pdb100_2021Mar03"
if [ ! -s $WDIR/$RPREFIX.hhr ]
then
    echo "Running hhsearch of JobId ${RPREFIX}"
    HH="hhsearch -b 50 -B 500 -z 50 -Z 500 -mact 0.05 -cpu $CPU -maxmem $MEM -aliw 100000 -e 100 -p 5.0 -d $DB"
    cat $WDIR/$RPREFIX.ss2 $WDIR/$RPREFIX.msa0.a3m > $WDIR/$RPREFIX.msa0.ss2.a3m
    $HH -i $WDIR/$RPREFIX.msa0.ss2.a3m -o $WDIR/$RPREFIX.hhr -atab $WDIR/$RPREFIX.atab -v 0 > $DIR_LOG/hhsearch.stdout 2> $DIR_LOG/hhsearch.stderr
fi


############################################################
# 4. predict distances and orientations
############################################################
if [ ! -s $WDIR/$RPREFIX.3track.npz ]
then
    echo "Predicting distance and orientations of JobId ${RPREFIX}"
    python $PIPEDIR/network/predict_pyRosetta.py \
        -m $WDIR/weights \
        -i $WDIR/$RPREFIX.msa0.a3m \
        -o $WDIR/$RPREFIX.3track \
        --hhr $WDIR/$RPREFIX.hhr \
        --atab $WDIR/$RPREFIX.atab \
        --db $DB 1> $DIR_LOG/network.stdout 2> $DIR_LOG/network.stderr
fi

############################################################
# 5. perform modeling
############################################################
mkdir -p $DIR_PDB3TRACK

conda deactivate
conda activate folding

for m in 0 1 2
do
    for p in 0.05 0.15 0.25 0.35 0.45
    do
        for ((i=0;i<1;i++))
        do
            if [ ! -f $DIR_PDB3TRACK/model${i}_${m}_${p}.pdb ]; then
                echo "python -u $PIPEDIR/folding/RosettaTR.py --roll -r 3 -pd $p -m $m -sg 7,3 $WDIR/$RPREFIX.3track.npz $IN $DIR_PDB3TRACK/model${i}_${m}_${p}.pdb"
            fi
        done
    done
done > $WDIR/parallel.fold.list

N=`cat $WDIR/parallel.fold.list | wc -l`
if [ "$N" -gt "0" ]; then
    echo "Running parallel RosettaTR.py"    
    parallel -j $CPU < $WDIR/parallel.fold.list > $DIR_LOG/folding.stdout 2> $DIR_LOG/folding.stderr
fi

############################################################
# 6. Pick final models
############################################################
count=$(find $DIR_PDB3TRACK -maxdepth 1 -name '*.npz' | grep -v 'features' | wc -l)
if [ "$count" -lt "15" ]; then
    # run DeepAccNet-msa
    echo "Running DeepAccNet-msa of JobId ${RPREFIX}"
    python $PIPEDIR/DAN-msa/ErrorPredictorMSA.py --roll -p $CPU $WDIR/$RPREFIX.3track.npz $DIR_PDB3TRACK $DIR_PDB3TRACK 1> $DIR_LOG/DAN_msa.stdout 2> $DIR_LOG/DAN_msa.stderr
fi

if [ ! -s $DIR_MODEL/model_5.crderr.pdb ]
then
    echo "Picking final models of JobId ${RPREFIX}"
    python -u -W ignore $PIPEDIR/DAN-msa/pick_final_models.div.py \
        $DIR_PDB3TRACK $DIR_MODEL $CPU > $DIR_LOG/pick.stdout 2> $DIR_LOG/pick.stderr
    echo "Final models saved in: ${DIR_MODEL}"
fi
echo "Done"
