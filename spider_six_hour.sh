#!/bin/sh

array=("spider.sh" "__init__.py" "__pycache__", "spider_six_hour.sh", "stats_three_half.sh")

#日本語サイト
cd /var/www/crawlers/scrapy/jp/jp/spiders
for file in `ls`; do
  if ! `echo ${array[*]} | grep -q "$file"` ; then
    nohup scrapy crawl ${file/.py/} > /dev/null &
  fi
done

#英語サイト
cd /var/www/crawlers/scrapy/en/en/spiders
for file in `ls`; do
  if ! `echo ${array[*]} | grep -q "$file"` ; then
    nohup scrapy crawl ${file/.py/} > /dev/null &
  fi
done

#selenium必須サイト
cd /var/www/crawlers/selenium/jp
for file in `ls`; do
  if ! `echo ${array[*]} | grep -q "$file"` ; then
    python3 ${file} > /dev/null &
    pid=$!
    wait $pid
  fi
done

cd /var/www/crawlers/tournament/mtgtopeight
python3 mtgtopeight_excute.py  >> /var/log/mtgtopeight.log 2>> /var/log/mtgtopeight_error.log &
