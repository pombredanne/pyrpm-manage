#!/bin/sh
for i in *.py
do
	echo $i
	expand -i -t 4 $i > $i.t
	cat $i.t > $i
	rm -f $i.t
done
