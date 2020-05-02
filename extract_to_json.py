import json
import pandas as pd
from bs4 import BeautifulSoup

import os
from os.path import isfile, isdir, join, exists

class ExtractToJSON(object):
	"""docstring for ExtractToJSON"""
	def __init__(self, dir_path="YouTubeData"):
		super(ExtractToJSON, self).__init__()
		self._dir_path = dir_path
		self._dirs_dict = {
			'history': "history",
			'playlists': "playlists",
			'subscriptions': "subscriptions"
		}
		self._files_dict = {
			'search_history': "search-history.html",
			'watch_history': "watch-history.html"
		}

		if not isdir(dir_path):
			raise Exception('Enter an valid directory, "{}" directory doesnot exist!\n Create a directory "{}" in the current directory and put all the contents of "YouTube and YouTube Music" folder into this.'.format(dir_path, dir_path))

		if not exists("DataJSON"):
			os.mkdir("DataJSON")

		self._dirs = [f for f in os.listdir(dir_path) if isdir(join(dir_path, f))]

	def load_json(self, filename):
		with open(filename, 'r') as f:
			return json.load(f)

	def get_watch_history_json(self):
		history_list = []
		if self._dirs_dict['history'] in self._dirs:
			file_path = self._dir_path+"/"+self._dirs_dict['history']+"/"+self._files_dict['watch_history']
			print("Reading {}, this may take a while.".format(self._files_dict['watch_history']))
			file = open(file_path, "r")
			soup = BeautifulSoup(file, "html.parser")
			print("Created BeautifulSoup object.")

			entities = soup.body.div.findAll('div', {"class": "mdl-grid"})
			print("Videos count: {}".format(len(entities)))

			skipped = 0	
			for entity in entities:
				try:
					divs = entity.findAll('div')
					links = divs[1].findAll('a')
					entity_dict = {
						'source': divs[0].p.text,
						'video_title':links[0].text,
						'video_url':links[0]['href'],
						'channel_title':links[1].text,
						'channel_url':links[1]['href'],
						'timestamp': divs[1].text.split(links[1].text)[-1]
					}
					history_list.append(entity_dict)
				except:
					skipped+=1
			print("Skipped entities: {}".format(skipped))

			with open('DataJSON/watch_history.json', 'w') as f:
			     json.dump(history_list, f, ensure_ascii=False, indent=4)
			print("JSON file saved to DataJSON/watch_history.json")
		else:
			print("No history directory in YouTubeData directory")
		return history_list

	def get_watch_history_stats_json(self):
		if not exists("DataJSON/watch_history.json"):
			history_list = self.get_watch_history_json()
		else:
			history_list = self.load_json("DataJSON/watch_history.json")

		history_df = pd.DataFrame(history_list)
		channel_list = list(set(history_df['channel_title'].tolist()))
		unique_videos = list(set(history_df['video_title'].tolist()))

		history_stats_dict = {
			'videos': {
				'total_video_count': len(history_list),
				'unique_video_count': len(unique_videos)
			},
			'channels': {
				'channel_count': len(channel_list),
				'channel_list': channel_list
			}
		}

		for channel in channel_list:
			matched_df = history_df.loc[history_df['channel_title'] == channel]
			history_stats_dict['channels'][channel] = {
				'view_count': matched_df.shape[0],
				'videos_list': list(set(matched_df['video_title'])),
				'url': matched_df['channel_url'].tolist()[0]
			}

		for video in unique_videos:
			matched_df = history_df.loc[history_df['video_title'] == video]
			history_stats_dict['videos'][video] = {
				'view_count': matched_df.shape[0],
				'url': matched_df['video_url'].tolist()[0]
			}

		with open('DataJSON/watch_history_stats.json', 'w') as f:
		     json.dump(history_stats_dict, f, ensure_ascii=False, indent=4)
		print("JSON file saved to DataJSON/watch_history_stats.json")

if __name__ == '__main__':
	data_obj = ExtractToJSON(dir_path="YouTubeData")
	data_obj.get_watch_history_stats_json()