#!/bin/sh

#deck categorize
cd /var/www/crawlers/batch/deck_categorizer/
python3 deck_categorizer_all.py  >> /var/log/modaily/mo_standard.log 2>> /var/log/modaily/categorizer.log &
pid4=$!
wait $pid4

#カード情報
cd /var/www/crawlers/batch/card_obtainer/
python3 card_obtainer.py >> /var/log/cards.log 2>> /var/log/cards_error.log &
pid1=$!
wait $pid1

#画像収集
cd /var/www/crawlers/batch/card_image_obtainer/
python3 main.py >> /var/log/card_image.log 2>> /var/log/card_image_error.log &
pid3=$!
wait $pid3