# asr_utils.py
import librosa
import numpy as np

def load_audio(audio_path, sr=16000):
    """
    加载音频文件
    audio_path: 文件路径
    sr: 采样率
    return: numpy array, sr
    """
    audio, sr_ret = librosa.load(audio_path, sr=sr)
    return audio, sr_ret

def normalize_audio(audio_array):
    """
    归一化音频到 [-1, 1]
    audio_array: numpy array
    """
    if np.max(np.abs(audio_array)) > 0:
        audio_array = audio_array / np.max(np.abs(audio_array))
    return audio_array
