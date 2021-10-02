#!/bin/bash

python3 jobpoll.py

IS_ARRIVING = awk -F '=' '/\[jobpoll\]/{a=1}a==1&&$1~/arriving/{print $2;exit}' hackjob.ini
SEQ_STR = awk -F '=' '/\[jobpoll\]/{a=1}a==1&&$1~/seqstr/{print $2;exit}' hackjob.ini
CUR_JOBID = awk -F '=' '/\[jobpoll\]/{a=1}a==1&&$1~/curjobid/{print $2;exit}' hackjob.ini

echo $SEQ_STR>>"input"$CUR_JOBID".fa"
#sbatch runjob.sh $CUR_JOBID
echo "sbatch runjob..."

python3 jobtag.py $CUR_JOBID
