#!/bin/bash

/opt/spark/bin/spark-submit \
  --master local[*] \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,org.postgresql:postgresql:42.7.3 \
  /home/sabya/2025EM1100189/food_delivery_streaming/local/producers/orders_cdc_producer.py \
  --config /home/sabya/2025EM1100189/food_delivery_streaming/local/configs/orders_stream.yml
