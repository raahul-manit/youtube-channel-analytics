from googleapiclient.discovery import build
import pandas as pd
import matplotlib.pyplot as plt
import re

API_KEY = "AIzaSyAq56aE6TGN7dE3-EtoL0-ht01Eza6gS04"

youtube = build('youtube', 'v3', developerKey=API_KEY)


def remove_emojis(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)


def get_channel_stats(channel_name):

    search = youtube.search().list(
        q=channel_name,
        part='snippet',
        type='channel',
        maxResults=1
    ).execute()

    channel_id = search['items'][0]['snippet']['channelId']

    response = youtube.channels().list(
        part='snippet,statistics,contentDetails',
        id=channel_id
    ).execute()

    data = dict(
        Channel_Name=response['items'][0]['snippet']['title'],
        Subscribers=response['items'][0]['statistics']['subscriberCount'],
        Views=response['items'][0]['statistics']['viewCount'],
        Total_Videos=response['items'][0]['statistics']['videoCount'],
        Playlist_ID=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    )

    return data


def get_video_ids(playlist_id):

    video_ids = []

    request = youtube.playlistItems().list(
        part='contentDetails',
        playlistId=playlist_id,
        maxResults=50
    )

    response = request.execute()

    for item in response['items']:
        video_ids.append(item['contentDetails']['videoId'])

    return video_ids


def get_video_details(video_ids):

    all_data = []

    request = youtube.videos().list(
        part="snippet,statistics",
        id=",".join(video_ids[:20])
    )

    response = request.execute()

    for video in response['items']:

        title = remove_emojis(video['snippet']['title'])

        data = dict(
            Title=title,
            Views=int(video['statistics'].get('viewCount',0)),
            Likes=int(video['statistics'].get('likeCount',0)),
            Comments=int(video['statistics'].get('commentCount',0))
        )

        all_data.append(data)

    return all_data


channel_name = input("Enter YouTube Channel Name: ")

channel_data = get_channel_stats(channel_name)

print("\nChannel Name:", channel_data["Channel_Name"])
print("Subscribers:", channel_data["Subscribers"])
print("Total Views:", channel_data["Views"])
print("Total Videos:", channel_data["Total_Videos"])

video_ids = get_video_ids(channel_data["Playlist_ID"])

video_data = get_video_details(video_ids)

df = pd.DataFrame(video_data)

print("\nVideo Data:\n")
print(df)


top_views = df.sort_values(by="Views", ascending=False).head(10)

plt.figure()
plt.barh(top_views["Title"], top_views["Views"])
plt.title("Top 10 Videos by Views")
plt.tight_layout()
plt.show()


top_likes = df.sort_values(by="Likes", ascending=False).head(10)

plt.figure()
plt.barh(top_likes["Title"], top_likes["Likes"])
plt.title("Top 10 Videos by Likes")
plt.tight_layout()
plt.show()


top_comments = df.sort_values(by="Comments", ascending=False).head(10)

plt.figure()
plt.barh(top_comments["Title"], top_comments["Comments"])
plt.title("Top 10 Videos by Comments")
plt.tight_layout()
plt.show()