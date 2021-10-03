#!/bin/bash
python3 jobpoll.py

export ISARRIVING=`awk -F '=' '/\[jobpoll\]/{a=1}a==1&&$1~/arriving/{print $2;exit}' hackjob.ini`
export SEQSTR=`awk -F '=' '/\[jobpoll\]/{a=1}a==1&&$1~/seqstr/{print $2;exit}' hackjob.ini`
export CURJOBID=`awk -F '=' '/\[jobpoll\]/{a=1}a==1&&$1~/curjobid/{print $2;exit}' hackjob.ini`
echo $SEQSTR>>"input"$CUR_JOBID".fa"
echo $CURJOBID
echo $ISARRIVING
#sbatch runjob.sh $CURJOBID
echo "sbatch job..."
#python3 jobtag.py $CUR_JOBID