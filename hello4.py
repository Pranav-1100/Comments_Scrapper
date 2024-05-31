import os
import googleapiclient.discovery
import concurrent.futures
import time

youtube = None

def initialize_youtube(api_key):
    global youtube
    if youtube is None:
        youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)

def get_comments_page(video_id, page_token=None):
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        pageToken=page_token,
        maxResults=100
    )

    response = request.execute()
    comments = []
    next_page_token = response.get('nextPageToken')

    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
        comments.append(comment)

    return comments, next_page_token

def get_all_comments(video_id, api_key):
    initialize_youtube(api_key)
    comments = []
    page_token = None
    futures = []
    max_workers = 100
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_page_token = {executor.submit(get_comments_page, video_id, page_token): page_token}

        while future_to_page_token:
            done, _ = concurrent.futures.wait(future_to_page_token, return_when=concurrent.futures.FIRST_COMPLETED)

            for future in done:
                try:
                    fetched_comments, next_page_token = future.result()
                    comments.extend(fetched_comments)
                    if next_page_token:
                        future_to_page_token[executor.submit(get_comments_page, video_id, next_page_token)] = next_page_token
                except Exception as e:
                    print(f"An error occurred: {e}")

                del future_to_page_token[future]

    return comments

if __name__ == '__main__':
    VIDEO_ID = '25N0R1KnXVs'
    API_KEY = 'AIzaSyARwJY5D84cYjQ08dY7dx3T5KgA3M6cN8M'
    
    start_time = time.time()
    comments = get_all_comments(VIDEO_ID, API_KEY)
    end_time = time.time()
    
    with open('comments.txt', 'w', encoding='utf-8') as file:
        for comment in comments:
            file.write(comment + '\n')
    
    print(f"Total comments fetched: {len(comments)}")
    print(f"Time taken: {end_time - start_time} seconds")
