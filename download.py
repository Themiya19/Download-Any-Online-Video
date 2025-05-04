import yt_dlp
import os

def download_video(url, output_path='.'):
    try:
        # Configuration options for faster downloads
        ydl_opts = {
            'format': 'best',  # Download best quality
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',  # Output template
            'noplaylist': True,  # Download single video, not playlist
            
            # Speed optimization options
            'noprogress': False,  # Show progress bar
            'quiet': False,
            'verbose': False,
            'buffersize': 1024 * 1024 * 16,  # 16MB buffer size
            'http_chunk_size': 1024 * 1024 * 10,  # 10MB chunks
            
            # External downloader with multiple connections
            'external_downloader': 'aria2c',
            'external_downloader_args': [
                '--min-split-size=1M', 
                '--max-connection-per-server=16', 
                '--max-concurrent-downloads=16',
                '--split=16'
            ],
        }
        
        # Download the video
        print(f"Downloading video from: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print(f"Download completed! Saved as: {info.get('title', 'video')}.{info.get('ext', 'mp4')}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Ask user for video URL
    video_url = input("Enter the URL of the video you want to download: ")
    
    # Ask for custom output path (optional)
    custom_path = input("Enter output directory (press Enter for current directory): ")
    output_directory = custom_path if custom_path.strip() else '.'
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Created directory: {output_directory}")
    
    # Download the video
    download_video(video_url, output_directory)