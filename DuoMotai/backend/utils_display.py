# utils_display.py
import matplotlib.pyplot as plt
import numpy as np
import librosa.display

def plot_waveform(audio, sr):
    """绘制音频波形"""
    plt.figure(figsize=(10, 4))
    librosa.display.waveshow(audio, sr=sr)
    plt.title("Waveform")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    plt.show()

def plot_spectrogram(audio, sr):
    """绘制谱图"""
    stft = np.abs(librosa.stft(audio))
    db_spec = librosa.amplitude_to_db(stft, ref=np.max)
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(db_spec, sr=sr, x_axis="time", y_axis="hz")
    plt.title("Spectrogram")
    plt.colorbar(format="%+2.0f dB")
    plt.tight_layout()
    plt.show()

def print_table(data_dict):
    """以表格形式打印调试数据"""
    print("="*50)
    for k, v in data_dict.items():
        print(f"{k:20s} | {v}")
    print("="*50)
