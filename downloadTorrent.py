import yt_dlp
import os
import re
import subprocess
import bencodepy
import hashlib
import base64

def magnet_from_torrent(torrent_path):
    """Convert a torrent file to a magnet link"""
    try:
        with open(torrent_path, 'rb') as f:
            torrent_data = f.read()
        
        decoded = bencodepy.decode(torrent_data)
        info_hash = hashlib.sha1(bencodepy.encode(decoded[b'info'])).hexdigest()
        
        # Get the name from the torrent file
        name = decoded[b'info'].get(b'name', b'').decode('utf-8', errors='ignore')
        
        # Get trackers from the torrent
        trackers = []
        if b'announce' in decoded:
            trackers.append(decoded[b'announce'].decode('utf-8', errors='ignore'))
        if b'announce-list' in decoded:
            for tracker_list in decoded[b'announce-list']:
                for tracker in tracker_list:
                    trackers.append(tracker.decode('utf-8', errors='ignore'))
        
        # Build the magnet link
        magnet = f"magnet:?xt=urn:btih:{info_hash}&dn={name}"
        for tracker in trackers:
            if tracker:
                magnet += f"&tr={tracker}"
                
        return magnet
    except Exception as e:
        print(f"Error creating magnet link: {e}")
        return None

def download_torrent(torrent_path, output_path='.'):
    """Download content from a torrent file"""
    try:
        # Convert torrent to magnet link
        magnet_link = magnet_from_torrent(torrent_path)
        if not magnet_link:
            print("Failed to create magnet link from torrent file")
            return
        
        print(f"Generated magnet link: {magnet_link[:60]}...")
        
        # Use aria2c to download the torrent content
        command = [
            'aria2c',
            '--min-split-size=1M',
            '--max-connection-per-server=16',
            '--max-concurrent-downloads=16',
            '--split=16',
            '--seed-time=0',  # Don't seed after download completes
            '--dir', output_path,
            magnet_link
        ]
        
        print("Starting download with aria2c...")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Stream the output
        for line in process.stdout:
            print(line.strip())
            
        process.wait()
        
        if process.returncode == 0:
            print(f"Download completed! Files saved to: {output_path}")
        else:
            print(f"Download failed with return code: {process.returncode}")
            
    except Exception as e:
        print(f"An error occurred while downloading torrent: {e}")

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
    print("Choose download mode:")
    print("1. Download from URL (YouTube, etc.)")
    print("2. Download from torrent file")
    
    mode = input("Enter your choice (1 or 2): ")
    
    # Ask for custom output path (optional)
    custom_path = input("Enter output directory (press Enter for current directory): ")
    output_directory = custom_path if custom_path.strip() else '.'
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Created directory: {output_directory}")
    
    if mode == "1":
        # URL download mode
        video_url = input("Enter the URL of the video you want to download: ")
        download_video(video_url, output_directory)
    elif mode == "2":
        # Torrent download mode
        torrent_file = input("Enter the path to the torrent file: ")
        if os.path.exists(torrent_file):
            download_torrent(torrent_file, output_directory)
        else:
            print(f"Torrent file not found: {torrent_file}")
    else:
        print("Invalid choice. Please run the script again and select 1 or 2.")