#!/bin/bash
spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
  ~/2025EM1100189/food_delivery_streaming/local/consumers/orders_stream_consumer.py \
  --config ~/2025EM1100189/food_delivery_streaming/local/configs/orders_stream.yml
