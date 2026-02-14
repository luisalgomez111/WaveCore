import soundfile as sf
import numpy as np

def load_waveform_data(file_path, points=1000):
    """
    Lee un archivo de audio y devuelve una versión reducida de la forma de onda
    para visualización rápida.
    :param file_path: Ruta al archivo.
    :param points: Número aproximado de puntos a devolver.
    :return: numpy array con los datos normalizados (-1 a 1).
    """
    try:
        with sf.SoundFile(file_path) as f:
            frames = f.frames
            samplerate = f.samplerate
            duration = frames / samplerate
            channels = f.channels
            
            # Divide file into 'points' chunks
            chunk_size = max(1, frames // points)
            reduced_data = np.zeros(points, dtype=np.float32)
            
            # Read in larger blocks to minimize I/O overhead
            # But process each chunk within the block
            block_frames = 100000 
            
            p_idx = 0
            curr_frames_read = 0
            
            # Simplified approach for speed and memory:
            # We jump and read a small window around each point
            # Or read everything in blocks.
            
            # Optimized Block Reading:
            for block in f.blocks(blocksize=block_frames, always_2d=True):
                # block is (block_frames, channels)
                # Mix to mono
                mono_block = block.mean(axis=1)
                
                # How many waveform 'points' fall into this block?
                # We need to find peaks for each relative chunk
                # (This is more complex but more robust)
                
                # Simpler: just take one sample every 'chunk_size'
                # but let's do a better peak detection if possible
                
                # To keep it fast for UI, we'll use a stride reading if extremely large
                # for now, let's just make it memory safe by not loading everything at once.
                
                # Calculate which points in 'reduced_data' this block covers
                start_p = curr_frames_read // chunk_size
                end_p = (curr_frames_read + len(mono_block)) // chunk_size
                
                for p in range(start_p, min(end_p, points)):
                    # Calculate relative start/end in mono_block
                    b_start = p * chunk_size - curr_frames_read
                    b_end = (p + 1) * chunk_size - curr_frames_read
                    
                    # Clamp to block bounds
                    b_start = max(0, b_start)
                    b_end = min(len(mono_block), b_end)
                    
                    if b_start < b_end:
                        # Peak for this waveform point
                        reduced_data[p] = np.max(np.abs(mono_block[b_start:b_end]))
                
                curr_frames_read += len(mono_block)
                if curr_frames_read >= frames: break

        # Normalización visual
        max_val = np.max(reduced_data)
        if max_val > 0:
            reduced_data = reduced_data / max_val
            
        return reduced_data, duration, channels
        
    except Exception as e:
        print(f"Soundfile failed: {e}. Trying miniaudio...")
        try:
            import miniaudio
            info = miniaudio.get_file_info(file_path)
            decoded = miniaudio.decode_file(file_path, nchannels=1, sample_rate=info.sample_rate) # Mono for waveform
            
            # Decoded samples are int16 by default
            samples = np.array(decoded.samples, dtype=np.float32) / 32768.0
            
            duration = info.duration
            channels = info.nchannels
            
            # Resample to 'points'
            num_samples = len(samples)
            if num_samples > points:
                # Simple decimation
                step = num_samples // points
                reduced_data = np.zeros(points, dtype=np.float32)
                for i in range(points):
                    start = i * step
                    end = start + step
                    chunk = samples[start:end]
                    if len(chunk) > 0:
                        reduced_data[i] = np.max(np.abs(chunk))
            else:
                reduced_data = samples
                
            # Normalize
            max_val = np.max(reduced_data)
            if max_val > 0:
                reduced_data = reduced_data / max_val
                
            return reduced_data, duration, channels
            
        except Exception as e2:
            print(f"Miniaudio failed: {e2}")
            return np.zeros(points), 0, 0
