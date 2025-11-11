# modules/tts/tts_service.py
import os
import sys
import subprocess
import threading
import time
import re
import logging
from typing import Optional

# 检查各种本地TTS是否可用
ESPEAK_AVAILABLE = False
FESTIVAL_AVAILABLE = False
PYGAME_INITIALIZED = False  # 添加pygame初始化状态跟踪

try:
    subprocess.run(["espeak", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ESPEAK_AVAILABLE = True
except (subprocess.CalledProcessError, FileNotFoundError):
    ESPEAK_AVAILABLE = False

try:
    subprocess.run(["festival", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    FESTIVAL_AVAILABLE = True
except (subprocess.CalledProcessError, FileNotFoundError):
    FESTIVAL_AVAILABLE = False

logger = logging.getLogger(__name__)

class TTSService:
    """
    语音合成服务模块（Text-To-Speech）
    支持：
      ✅ 本地 IndexTTS 模型（通过 ModelScope）
      ✅ Google TTS 作为回退
      ✅ eSpeak 和 Festival 作为备用方案
    """
    def __init__(self, engine: str = "local", voice: Optional[str] = None, rate: int = 180,
                 output_dir: str = "outputs/tts", model_path: Optional[str] = None):
        self.engine = engine
        self.voice = voice
        self.rate = rate
        self.output_dir = output_dir
        self.model_path = model_path or "/mnt/data/modelscope_cache/hub/pengzhendong"
        self.is_speaking = False
        self.speak_thread = None
        self.current_playback_thread = None  # 添加当前播放线程跟踪
        self.should_stop_playback = False    # 添加播放中断标志
        os.makedirs(output_dir, exist_ok=True)

        # 初始化 IndexTTS 模型
        self.index_tts = None
        if self.engine == "local":
            self._load_index_tts_model()

    # ============================================================
    # 模型加载
    # ============================================================
    def _load_index_tts_model(self):
        """
        尝试通过 ModelScope 加载本地 IndexTTS 模型
        """
        try:
            import torch
            from modelscope.pipelines import pipeline
            from modelscope.utils.constant import Tasks

            self.device = "cuda" if torch.cuda.is_available() else "cpu"

            print(f"[TTS] 🔄 正在加载 IndexTTS 模型（{self.device}）: {self.model_path}")
            # 修复：明确指定task参数为字符串
            self.index_tts = pipeline(
                task=Tasks.text_to_speech,  # 修复NoneType错误
                model=self.model_path,
                device=self.device
            )
            print(f"[TTS] ✅ IndexTTS 模型加载成功！")
        except Exception as e:
            print(f"[TTS] ❌ IndexTTS 模型加载失败: {e}")
            self.index_tts = None

    # ============================================================
    # 主合成函数
    # ============================================================
    def synthesize(self, text: str, filename: str = "speech.wav") -> str:
        """
        将文本合成为语音文件，返回音频路径
        """
        if not self._is_valid_text(text):
            print(f"[TTSService] ⚠️ 无效文本，跳过合成: {text}")
            return ""

        output_path = os.path.join(self.output_dir, filename)

        # 根据可用的TTS引擎选择合适的合成方式
        if self.engine == "local" and self.index_tts:
            self._synthesize_with_index_tts(text, output_path)
        elif ESPEAK_AVAILABLE:
            self._synthesize_with_espeak(text, output_path)
        elif FESTIVAL_AVAILABLE:
            self._synthesize_with_festival(text, output_path)
        else:
            self._synthesize_with_gtts(text, output_path)

        print(f"[TTSService] ✅ 生成语音文件: {output_path}")
        return output_path

    # ============================================================
    # 文本过滤
    # ============================================================
    def _is_valid_text(self, text: str) -> bool:
        """
        检查文本是否为有效内容（防止 TTS 播放垃圾字符）
        """
        if not text or not text.strip():
            return False

        meaningless_patterns = [
            r".*chinese\s+letter.*",
            r".*try\s+these\s+letter.*",
            r".*chi\s+these\s+letter.*",
            r".*tidy.*",
            r"^\s*[a-zA-Z]\s*$",
            r".*these\s+letter.*"
        ]

        text_lower = text.lower()
        for pattern in meaningless_patterns:
            if re.match(pattern, text_lower):
                return False

        # 检查是否包含中文字符
        if re.search(r'[\u4e00-\u9fff]', text):
            return True
            
        # 检查是否包含价格信息
        if re.search(r'[¥$€£₹]\d+|\d+\s*[元块]', text):
            return True
            
        # 检查是否包含重要短语
        important_phrases = ['亲亲', '为您找到', '价格', '商品']
        if any(phrase in text for phrase in important_phrases):
            return True
            
        # 检查长度和基本内容
        if len(text) > 5 and not re.match(r'^[a-zA-Z\s]+$', text):
            return True
            
        return False

    # ============================================================
    # 使用本地 IndexTTS
    # ============================================================
    def _synthesize_with_index_tts(self, text: str, output_path: str):
        """
        使用 ModelScope 加载的 IndexTTS 模型进行合成
        """
        try:
            result = self.index_tts(input=text)
            audio_bytes = result["output_wav"]
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            print(f"[TTS] 🗣️ IndexTTS 本地合成成功 → {output_path}")
        except Exception as e:
            print(f"[TTS] ❌ IndexTTS 合成失败: {e}")
            print("[TTS] ⚙️ 回退至 Google TTS")
            self._synthesize_with_gtts(text, output_path)

    # ============================================================
    # 使用 eSpeak
    # ============================================================
    def _synthesize_with_espeak(self, text: str, output_path: str):
        """
        使用 eSpeak 合成语音
        """
        try:
            cmd = ["espeak", "-v", "zh", "-s", "150", "-w", output_path, text]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"[TTS] 🗣️ eSpeak 合成成功 → {output_path}")
        except Exception as e:
            print(f"[TTS] ❌ eSpeak 合成失败: {e}")
            self._synthesize_with_gtts(text, output_path)

    # ============================================================
    # 使用 Festival
    # ============================================================
    def _synthesize_with_festival(self, text: str, output_path: str):
        """
        使用 Festival 合成语音
        """
        try:
            cmd = f'echo "{text}" | text2wave -o {output_path}'
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"[TTS] 🗣️ Festival 合成成功 → {output_path}")
        except Exception as e:
            print(f"[TTS] ❌ Festival 合成失败: {e}")
            self._synthesize_with_gtts(text, output_path)

    # ============================================================
    # 使用 Google TTS
    # ============================================================
    def _synthesize_with_gtts(self, text: str, output_path: str):
        """
        使用 Google TTS 合成语音（在线）
        """
        try:
            from gtts import gTTS
            if not text or not text.strip():
                text = " "
            # 明确指定使用中文语言参数
            tts = gTTS(text=text, lang='zh-CN', slow=False, lang_check=False)
            tts.save(output_path)
            print(f"[TTS] 🌐 Google TTS 合成完成 → {output_path}")
        except Exception as e:
            print(f"[TTS] ❌ Google TTS 合成失败: {e}")

    # ============================================================
    # 播放接口
    # ============================================================
    def speak(self, text: str, filename: str = "speech.wav") -> str:
        return self.synthesize(text, filename)

    def speak_and_play(self, text: str, filename: str = "speech.wav"):
        """
        异步合成并播放
        """
        if not self._is_valid_text(text):
            print(f"[TTSService] 无效文本，跳过播放: {text}")
            return

        # 中断当前播放
        self.should_stop_playback = True
        if self.current_playback_thread and self.current_playback_thread.is_alive():
            self.current_playback_thread.join(timeout=1.0)  # 等待最多1秒
        
        # 启动新的播放线程
        self.current_playback_thread = threading.Thread(target=self._speak_and_play_thread, args=(text, filename))
        self.current_playback_thread.daemon = True
        self.current_playback_thread.start()

    def _speak_and_play_thread(self, text: str, filename: str):
        # 不检查播放状态，允许连续播放
        self.should_stop_playback = False
        try:
            audio_path = self.speak(text, filename)
            if not audio_path or self.should_stop_playback:
                return
            self._play_audio(audio_path)
        except Exception as e:
            print(f"[TTSService] 播放音频时出错: {e}")

    def _play_audio(self, audio_path: str):
        """
        播放音频文件（兼容Linux/macOS/Windows）
        """
        global PYGAME_INITIALIZED
        
        # 检查是否需要中断播放
        if self.should_stop_playback:
            return
            
        try:
            # 检查文件是否存在且不为空
            if not os.path.exists(audio_path):
                print(f"[TTS] ⚠️ 音频文件不存在: {audio_path}")
                return
                
            if os.path.getsize(audio_path) == 0:
                print(f"[TTS] ⚠️ 音频文件为空: {audio_path}")
                return
            
            # 尝试使用pygame播放
            try:
                import pygame
                # 修复：使用全局状态跟踪pygame初始化，避免重复初始化
                if not PYGAME_INITIALIZED:
                    pygame.mixer.init()
                    PYGAME_INITIALIZED = True
                
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy() and not self.should_stop_playback:
                    time.sleep(0.1)
                    
                # 修复：使用fadeout避免可能的内存问题
                if not self.should_stop_playback:
                    pygame.mixer.music.fadeout(100)
                    time.sleep(0.2)  # 等待fadeout完成
                else:
                    pygame.mixer.music.stop()
                print(f"[TTS] ✅ 使用pygame成功播放音频: {audio_path}")
                return
            except ImportError:
                print("[TTS] ⚠️ pygame未安装，尝试其他播放方式")
            except Exception as e:
                print(f"[TTS] ⚠️ pygame播放失败: {e}")
                # 确保在出错时也清理资源
                try:
                    if 'pygame' in locals():
                        pygame.mixer.quit()
                        PYGAME_INITIALIZED = False
                except:
                    pass
            
            # 尝试使用playsound
            try:
                import playsound
                # 检查是否需要中断播放
                if not self.should_stop_playback:
                    playsound.playsound(audio_path)
                print(f"[TTS] ✅ 使用playsound成功播放音频: {audio_path}")
                return
            except ImportError:
                print("[TTS] ⚠️ playsound未安装，尝试系统播放器")
            except Exception as e:
                print(f"[TTS] ⚠️ playsound播放失败: {e}")
            
            # 尝试系统播放器
            if sys.platform == "win32":
                # 检查是否需要中断播放
                if not self.should_stop_playback:
                    os.startfile(audio_path)
                print(f"[TTS] ✅ 使用系统默认播放器成功播放音频: {audio_path}")
            elif sys.platform == "darwin":
                # 检查是否需要中断播放
                if not self.should_stop_playback:
                    subprocess.call(["afplay", audio_path])
                print(f"[TTS] ✅ 使用afplay成功播放音频: {audio_path}")
            else:  # Linux系统
                # 尝试使用多种播放器
                players = ["paplay", "aplay", "mpg123", "ffplay", "vlc"]
                player_found = False
                for player in players:
                    try:
                        # 检查播放器是否存在
                        subprocess.run(["which", player], check=True, stdout=subprocess.DEVNULL)
                        print(f"[TTS] 使用播放器: {player}")
                        # 检查是否需要中断播放
                        if not self.should_stop_playback:
                            if player == "paplay":
                                subprocess.run([player, "--file-format=wav", audio_path])
                            elif player == "aplay":
                                subprocess.run([player, "-f", "cd", audio_path])
                            elif player == "ffplay":
                                subprocess.run([player, "-nodisp", "-autoexit", audio_path], 
                                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            elif player == "vlc":
                                subprocess.run([player, "--play-and-exit", audio_path], 
                                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            else:
                                subprocess.run([player, audio_path])
                        player_found = True
                        print(f"[TTS] ✅ 使用{player}成功播放音频: {audio_path}")
                        break  # 成功播放就跳出循环
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue  # 尝试下一个播放器
                
                if not player_found:
                    print("[TTS] ⚠️ 未找到可用的音频播放器，请安装以下任一播放器: paplay, aplay, mpg123, ffplay, vlc")
        except Exception as e:
            print(f"[TTS] ❌ 播放音频失败: {e}")

    def play_welcome_message(self):
        """
        播报欢迎消息："亲亲你想买什么"
        """
        welcome_text = "亲亲你想买什么"
        self.speak_and_play(welcome_text, "welcome.wav")

    def play_product_info(self, product_info: dict):
        """
        播报商品信息
        :param product_info: 商品信息字典，应包含name和price字段
        """
        if not product_info or not isinstance(product_info, dict):
            return
            
        product_name = product_info.get("name", "未知商品")
        product_price = product_info.get("price", "未知价格")
        product_description = product_info.get("description", "")
        
        # 构造商品信息播报文本
        info_text = f"为您找到{product_name}, 价格{product_price}, {product_description}"
        filename = f"product_{int(time.time())}.wav"
        
        self.speak_and_play(info_text, filename)

    def cleanup(self):
        """
        清理资源，特别是pygame资源
        """
        global PYGAME_INITIALIZED
        try:
            import pygame
            if PYGAME_INITIALIZED:
                pygame.mixer.quit()
                PYGAME_INITIALIZED = False
                print("[TTS] ✅ Pygame资源已清理")
        except:
            pass
