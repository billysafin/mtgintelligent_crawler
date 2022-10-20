#!/bin/sh

#集計
cd /var/www/crawlers/batch/mtg_card_usage_aggregate/
python3 aggregate.py  >> /var/log/aggregate.log 2>> /var/log/aggregate_error.log &

#集計
cd /var/www/crawlers/batch/mtg_deck_count_by_date_aggregate/
python3 aggregate.py  >> /var/log/aggregate.log 2>> /var/log/aggregate_error.log &
pid2=$!
wait $pid2
