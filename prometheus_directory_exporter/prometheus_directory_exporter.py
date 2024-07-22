#!/usr/bin/python3
import os
import time
from datetime import datetime, timedelta
from prometheus_client import start_http_server, Gauge

#Define the metric
MOST_RECENT_FILE_EXISTS = Gauge('directory_not_updated', 'Indicates if a directory has not been updated in the last X minutes', ['directory'])

CHANNEL_NAME = ['EXAMPLE 1', 'example_1']

CHANNEL_CODE = ['0041', '0095']
HARDWARE = 'VBR0500ABR064'

BASE_PATH = r'/mnt/57/MP4 FILES/'

#Vi004120240721104000104500000100.mp4

def construct_directory_name():
  today = datetime.now().strftime('%Y%m%d')
  year = today[:4]
  year_month = today[:6]

  directories = []
  for chan, code in zip(CHANNEL_NAME, CHANNEL_CODE):
      print({chan}, {code})
      dir_path = os.path.join(
        BASE_PATH,
        chan,
        HARDWARE,
        f'Vi{code}{year}',
        f'Vi{code}{year_month}',
        f'Vi{code}{today}'
      )
      directories.append(dir_path)
  #print(directories)
  return directories

def construct_expected_filename(code):
  now = datetime.now()
  rounded_time = now - timedelta(minutes=now.minute % 5, seconds=now.second, microseconds=now.microsecond)
  #print('Rounded time: ', rounded_time)
  five_minutes_ago = rounded_time - timedelta(minutes=5)
  #print('five_minutes_ago: ',five_minutes_ago)

  today = now.strftime('%Y%m%d')
  hour_now = rounded_time.strftime('%H')
  minute_rounded = rounded_time.strftime('%M')

  if rounded_time.minute < 5:
    hour_five_minutes_ago = (rounded_time - timedelta(hours=1)).strftime('%H')
  else:
    hour_five_minutes_ago = hour_now

  minute_five_minutes_ago = five_minutes_ago.strftime('%M')

  filename = f'Vi{code}{today}{hour_five_minutes_ago}{minute_five_minutes_ago}00{hour_now}{minute_rounded}00000100.mp4'
  #print('Filename: ', filename)
  return filename


def check_directories():
    directories_to_monitor = construct_directory_name()

    for directory in directories_to_monitor:
      code = directory.split('/')[-1][2:6]
      #print(code)
      expected_filename = construct_expected_filename(code)
      expected_filepath = os.path.join(directory, expected_filename)
      print(expected_filepath)

      if os.path.isfile(expected_filepath):
        MOST_RECENT_FILE_EXISTS.labels(directory=directory).set(1)
      else:
        MOST_RECENT_FILE_EXISTS.labels(directory=directory).set(0)

if __name__ == '__main__':
     start_http_server(8000)
     print("Prometheus exporter started on port 8000")

     while True:
       check_directories()
       time.sleep(60)
