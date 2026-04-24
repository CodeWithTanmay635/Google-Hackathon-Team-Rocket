#!/usr/bin/env python3
"""
SmartRoad AI - Pothole CCTV Image Scraper
Scrapes pothole images from Google Images with CCTV/road camera perspective.
Requires: pip install googlesearch-python pillow requests opencv-python
Usage: python pothole_scraper.py --query "pothole CCTV" --num 100
"""

import os
import requests
from PIL import Image
import cv2
import numpy as np
from googlesearch import search
import argparse
import time
from urllib.parse import urlparse
from datetime import datetime
import hashlib
import json

def create_dataset_dir():
    """Create raw_cctv_potholes directory if it doesn't exist."""
    dataset_dir = 'raw_cctv_potholes'
    os.makedirs(dataset_dir, exist_ok=True)
    print(f"📁 Dataset directory: {os.path.abspath(dataset_dir)}/")
    return dataset_dir

def is_valid_image_size(image_path, min_width=480, min_height=360):
    """Check if image meets minimum size for CCTV quality."""
    try:
        img = Image.open(image_path)
        width, height = img.size
        return width >= min_width and height >= min_height
    except:
        return False

def simulate_cctv_crop(img_path):
    """Crop image to simulate CCTV top-down road view (center 70% area)."""
    img = cv2.imread(img_path)
    if img is None:
        return None
    
    h, w = img.shape[:2]
    crop_h = int(h * 0.7)
    crop_w = int(w * 0.7)
    start_y = (h - crop_h) // 2
    start_x = (w - crop_w) // 2
    
    cropped = img[start_y:start_y+crop_h, start_x:start_x+crop_w]
    return cropped

def download_image(url, dataset_dir, query, max_retries=3):
    """Download and validate single image."""
    for attempt in range(max_retries):
        try:
            # Get filename from URL or hash it
            domain = urlparse(url).netloc
            filename = hashlib.md5(url.encode()).hexdigest()[:8] + f"_{int(time.time())}"
            ext = os.path.splitext(urlparse(url).path)[1] or '.jpg'
            filepath = os.path.join(dataset_dir, f"{filename}{ext}")
            
            resp = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            resp.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(resp.content)
            
            # Validate
            if os.path.getsize(filepath) > 10*1024 and is_valid_image_size(filepath):  # >10KB
                print(f"✅ Downloaded: {os.path.basename(filepath)} ({os.path.getsize(filepath)//1024}KB) from {domain}")
                # Simulate CCTV crop
                cropped_path = filepath.replace(f".{ext}", f"_cctv{ext}")
                cropped_img = simulate_cctv_crop(filepath)
                if cropped_img is not None:
                    cv2.imwrite(cropped_path, cropped_img)
                    os.remove(filepath)  # Replace original with cropped
                    print(f"   ↳ CCTV-cropped: {os.path.basename(cropped_path)}")
                return True
            else:
                os.remove(filepath)
                print(f"❌ Invalid size: {url[:60]}...")
        except Exception as e:
            print(f"⚠️ Download failed (attempt {attempt+1}): {str(e)[:50]}...")
            time.sleep(1)
    return False

def scrape_potholes(query, num_images=100, delay=1.0):
    """Main scraping function."""
    dataset_dir = create_dataset_dir()
    downloaded = 0
    failed = 0
    
    print(f"🔍 Searching Google Images for: '{query}' (target: {num_images} images)")
    print(f"⏳ Delay between requests: {delay}s | Starting...\n")
    
    for url in search(f"{query} filetype:jpg OR filetype:png OR filetype:jpeg", 
                      num_results=num_images*3,  # Oversample for quality
                      lang='en'):
        if downloaded >= num_images:
            break
            
        print(f"[{downloaded+1}/{num_images}] Checking: {url[:80]}...")
        
        if download_image(url, dataset_dir, query):
            downloaded += 1
        else:
            failed += 1
        
        time.sleep(delay)  # Rate limiting
    
    # Summary
    total_files = len([f for f in os.listdir(dataset_dir) if f.lower().endswith(('.jpg','.jpeg','.png'))])
    print("\n🎉 Scraping complete!")
    print(f"✅ Successfully downloaded: {downloaded}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total images in dataset: {total_files}")
    print(f"📂 Location: {os.path.abspath(dataset_dir)}/")
    
    # Generate metadata
    metadata = {
        'scraped_at': datetime.now().isoformat(),
        'query': query,
        'target_count': num_images,
        'downloaded': downloaded,
        'sources': list(set([f.split('_')[0] for f in os.listdir(dataset_dir) if 'cctv' in f.lower()]))[:5]
    }
    with open(os.path.join(dataset_dir, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
    print("📋 Metadata saved: metadata.json")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape pothole CCTV images')
    parser.add_argument('--query', default='pothole CCTV road camera overhead traffic view', 
                       help='Search query (default: pothole CCTV road camera...)')
    parser.add_argument('--num', type=int, default=100, 
                       help='Number of images to download (default: 100)')
    parser.add_argument('--delay', type=float, default=1.0, 
                       help='Delay between requests in seconds (default: 1.0)')
    
    args = parser.parse_args()
    scrape_potholes(args.query, args.num, args.delay)

