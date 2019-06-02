#!/bin/sh
python3 generate_celcom_owl_overall.py -o subject -n
echo "subject.pickle updated"
python3 generate_celcom_owl_overall.py -o name_predicate --combine name_predicate
echo "name_predicate.pickle update"
