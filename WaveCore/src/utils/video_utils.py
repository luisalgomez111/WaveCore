import cv2
import os
import hashlib

class VideoMetadataExtractor:
    def __init__(self, cache_dir_name="thumbnails"):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.cache_dir = os.path.join(self.base_dir, "cache", cache_dir_name)
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_metadata(self, video_path):
        """
        Extracts duration, width, height, fps, and a thumbnail path.
        Returns a dict.
        """
        if not os.path.exists(video_path):
            return {}

        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {}

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            duration = 0
            if fps > 0:
                duration = frame_count / fps

            # Generate Thumbnail
            thumb_path = self._generate_thumbnail(cap, video_path, frame_count)

            cap.release()

            return {
                "duration": duration,
                "width": width,
                "height": height,
                "fps": fps,
                "thumbnail_path": thumb_path
            }
        except Exception as e:
            print(f"Video Extraction Error ({video_path}): {e}")
            return {}

    def _generate_thumbnail(self, cap, video_path, frame_count):
        # Create a unique filename for the thumbnail based on video path
        hash_name = hashlib.md5(video_path.encode('utf-8')).hexdigest()
        thumb_filename = f"{hash_name}.jpg"
        thumb_path = os.path.join(self.cache_dir, thumb_filename)

        # Return existing if found
        if os.path.exists(thumb_path):
            return thumb_path

        # Seek to 20% of the video or 1 second, to avoid black start frames
        target_frame = 0
        if frame_count > 100:
            target_frame = int(frame_count * 0.1) # 10%
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()
        
        if ret:
            # Resize for efficiency (max 320 width)
            h, w = frame.shape[:2]
            if w > 320:
                new_w = 320
                new_h = int(h * (320 / w))
                frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
            
            cv2.imwrite(thumb_path, frame)
            return thumb_path
        
        return ""

import subprocess
import uuid
from utils.audio_loader import load_waveform_data

def get_video_waveform(video_path, points=800):
    temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache", "temp_waves")
    os.makedirs(temp_dir, exist_ok=True)
    
    unique_name = f"{uuid.uuid4()}.wav"
    temp_wav = os.path.join(temp_dir, unique_name)
    
    try:
        # ffmpeg -i input -vn -acodec pcm_s16le -ar 11025 -ac 1 output.wav
        cmd = [
            'ffmpeg', '-y', '-i', video_path,
            '-vn', '-acodec', 'pcm_s16le', '-ar', '11025', '-ac', '1',
            temp_wav
        ]
        
        # Check if ffmpeg is in path, or try strict path if known? 
        # For now assume PATH.
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        if os.path.exists(temp_wav):
            data, duration, _ = load_waveform_data(temp_wav, points)
            return data, duration
            
    except Exception as e:
        print(f"Waveform Extraction Error: {e}")
        
    finally:
        if os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except:
                pass
                
    return None, 0
