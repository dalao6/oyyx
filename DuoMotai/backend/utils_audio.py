# utils_audio.py
import numpy as np
import soundfile as sf
import librosa

def load_audio(file_path, sr=16000):
    """加载音频文件并返回音频数据和采样率"""
    data, file_sr = sf.read(file_path)
    if file_sr != sr:
        data = librosa.resample(data, orig_sr=file_sr, target_sr=sr)
    return data, sr

def get_duration(file_path):
    """返回音频时长（秒）"""
    info = sf.info(file_path)
    return info.duration

def compute_mfcc(audio, sr, n_mfcc=13):
    """计算 MFCC 特征"""
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)
    return mfcc.T

def normalize_audio(audio):
    """归一化音频幅值"""
    return audio / np.max(np.abs(audio))
