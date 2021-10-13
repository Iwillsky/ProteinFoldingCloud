#!/bin/bash
python3 jobpoll.py

export ISARRIVING=`awk -F '=' '/\[jobpoll\]/{a=1}a==1&&$1~/arriving/{print $2;exit}' hackjob.ini`
export SEQSTR=`awk -F '=' '/\[jobpoll\]/{a=1}a==1&&$1~/seqstr/{print $2;exit}' hackjob.ini`
export CURJOBID=`awk -F '=' '/\[jobpoll\]/{a=1}a==1&&$1~/curjobid/{print $2;exit}' hackjob.ini`
export TCHECKIN=$(date "+%m%d%H%M%S")
export INPUT_FILENAME=input$TCHECKIN.fa
echo $INPUT_FILENAME
echo $SEQSTR>>$INPUT_FILENAME
echo $CURJOBID
echo $ISARRIVING
sbatch runjob.sh $TCHECKIN $INPUT_FILENAME
echo "sbatch job..."
python3 jobtag.py $CURJOBID
echo "job updated."
