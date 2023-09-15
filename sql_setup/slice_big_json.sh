#!/bin/bash

echo "Separating reviews into small files"
split -l 500000 -a 1 yelp_academic_dataset_review.json review_
echo "Separating user into small files"
split -l 200000 -a 1 yelp_academic_dataset_user.json user_
echo "Removing the big parent files"
rm yelp_academic_dataset_review.json
rm yelp_academic_dataset_user.json