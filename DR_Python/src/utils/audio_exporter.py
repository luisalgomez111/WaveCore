import os
import soundfile as sf
import numpy as np

def export_snippet(source_path, start_ms, end_ms, output_dir=None):
    """
    Slices the audio file from start_ms to end_ms and saves it to a temp file using soundfile.
    Exports as WAV to ensure compatibility without external FFmpeg dependency.
    """
    if not os.path.exists(source_path):
        return None
        
    try:
        # Load audio using soundfile
        # soundfile reads into numpy array (frames, channels)
        # always_2d=True ensures we handle mono/stereo consistently
        data, samplerate = sf.read(source_path, always_2d=True)
        
        # Calculate samples
        start_sample = int((start_ms / 1000.0) * samplerate)
        end_sample = int((end_ms / 1000.0) * samplerate)
        
        # Ensure bounds
        start_sample = max(0, start_sample)
        end_sample = min(len(data), end_sample)
        
        if start_sample >= end_sample:
            return None
            
        snippet_data = data[start_sample:end_sample]
        
        # Generate Output Path
        if output_dir is None:
            import tempfile
            output_dir = tempfile.gettempdir()
            
        filename = os.path.basename(source_path)
        name, _ = os.path.splitext(filename)
        # Always export as .wav for safety/speed without ffmpeg encoding
        new_name = f"{name}_snippet_{int(start_ms)}_{int(end_ms)}.wav"
        output_path = os.path.join(output_dir, new_name)
        
        # Write
        sf.write(output_path, snippet_data, samplerate)
        
        return output_path
        
    except Exception as e:
        print(f"Export error: {e}")
        return None
