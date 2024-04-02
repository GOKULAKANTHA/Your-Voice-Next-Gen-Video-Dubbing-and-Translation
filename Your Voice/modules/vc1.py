import os
import numpy as np
import librosa

def collect_voice_samples(input_folder):
    voice_samples = []
    for filename in os.listdir(input_folder):
        if filename.endswith('.wav'):  # Assuming voice samples are in WAV format
            filepath = os.path.join(input_folder, filename)
            # Load audio file and extract features
            waveform, sample_rate = librosa.load(filepath, sr=None)
            voice_samples.append((waveform, sample_rate))
    return voice_samples

def preprocess_data(voice_samples):
    processed_samples = []
    for waveform, sample_rate in voice_samples:
        # Perform feature extraction (e.g., spectrogram)
        spectrogram = librosa.feature.melspectrogram(y=waveform, sr=sample_rate, n_fft=1024, hop_length=256)
        # Convert to decibels (log scale)
        spectrogram_db = librosa.power_to_db(spectrogram, ref=np.max)
        processed_samples.append(spectrogram_db)
    return processed_samples

# Example usage
input_folder = 'voices1'
voice_samples = collect_voice_samples(input_folder)
processed_samples = preprocess_data(voice_samples)
