import yt_dlp
import pandas as pd

# --- CONFIGURATION ---
CHANNELS = [
    "https://www.youtube.com/@MrBeast/videos?view=0&sort=p",
    "https://www.youtube.com/@veritasium/videos?view=0&sort=p"


    # add 8 more channel URLs here
]

# --- FUNCTION TO SCRAPE CHANNEL ---
def get_channel_videos(channel_url, top_n=10):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
        "forcejson": True,
    }

    results = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # extract channel info
        channel_info = ydl.extract_info(channel_url, download=False)
        channel_name = channel_info.get("title", "")
        subscribers = channel_info.get("channel_follower_count", "")

        # get video list
        entries = channel_info.get("entries", [])
        video_urls = [f"https://www.youtube.com/watch?v={v['id']}" for v in entries if v.get("id")]

        # get details of each video
        for i, video_url in enumerate(video_urls[:top_n]):
            try:
                vid = ydl.extract_info(video_url, download=False)
                results.append({
                    "Channel": channel_name,
                    "Subscribers": subscribers,
                    "Title": vid.get("title"),
                    "Views": vid.get("view_count"),
                    "Likes": vid.get("like_count"),
                    "Upload Date": vid.get("upload_date"),
                    "Video URL": video_url
                })
            except Exception as e:
                print(f"Error processing {video_url}: {e}")
    return results

# --- MAIN EXECUTION ---
all_videos = []
for ch in CHANNELS:
    print(f"Scraping: {ch}")
    all_videos.extend(get_channel_videos(ch, top_n=10))

# --- SAVE TO EXCEL ---
df = pd.DataFrame(all_videos)
df.to_excel("youtube_top10_videos.xlsx", index=False)
print("✅ Data saved to youtube_top10_videos.xlsx")
