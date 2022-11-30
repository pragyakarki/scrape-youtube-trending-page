import requests
import sys
import json
import time
import os
import argparse

current_dir = os.getcwd()

YOUTUBE_DATA_API_KEY_FOR_GITHUB_1 = os.environ['YOUTUBE_DATA_API_KEY_FOR_GITHUB_1']

country_list = ['IN', 'NP', 'US']


def api_request(page_token, country_code, api_key):
    video_resource = "id,snippet,contentDetails,status,statistics,player,topicDetails,recordingDetails,localizations"

    # Builds the URL and requests the JSON from it
    request_url = f"https://www.googleapis.com/youtube/v3/videos?part={video_resource}{page_token}chart=mostPopular&regionCode={country_code}&maxResults=50&key={api_key}"
    response = requests.get(request_url)

    print(
        f"{time.strftime('%Y-%m-%d %H:%M:%S')} :: RESPONSE Status-Code: {response.status_code} || Content-Type: {response.headers['content-type']}")
   
    if response.status_code == 429:
        print(
            f"{time.strftime('%Y-%m-%d %H:%M:%S')} :: Temporarily BANNED due to excess requests. EXITING...")
        sys.exit()
    return response.json()


def get_pages(country_code, api_key, next_page_token="&"):
    country_data = []
    while next_page_token is not None:
        video_data_page_json = api_request(
            next_page_token, country_code, api_key)
        next_page_token = video_data_page_json.get("nextPageToken", None)
        next_page_token = f"&pageToken={next_page_token}&" if next_page_token is not None else next_page_token

        items = video_data_page_json.get('items')
        # Handling :: TypeError: 'NoneType' object is not iterable
        # https://stackoverflow.com/questions/3887381/typeerror-nonetype-object-is-not-iterable-in-python
        if items is not None:
            for item in items:
                country_data.append(item)

    return country_data


def write_to_file(country_code, country_data):

    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} :: Writing {country_code} data to file...")

    executed_day = time.strftime('%y.%m.%d') # Create one folder for each day
    day_path = os.path.join(current_dir, executed_day)
    if not os.path.exists(day_path):
        os.makedirs(day_path)
    
    # Had to create subdirectories by hour since github has 1000 file limits per directory
    executed_hour = time.strftime('%y.%m.%d %H') # Create one folder for each hour
    path = os.path.join(day_path, executed_hour)
    if not os.path.exists(path):
        os.makedirs(path)
         
    with open(f"{path}/{time.strftime('%y.%m.%d %H.%M.%S')}_{country_code}_YouTube_Trending_Videos.json", "w+", encoding='utf-8') as file:
        json.dump(country_data, file, ensure_ascii=False, indent=4)
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} :: Done for {country_code}")


def get_data(country_codes, api_key):
    for country_code in country_codes:
        country_data = get_pages(country_code, api_key)
        write_to_file(country_code, country_data)


if __name__ == "__main__":
    get_data(country_list, YOUTUBE_DATA_API_KEY_FOR_GITHUB_1)
