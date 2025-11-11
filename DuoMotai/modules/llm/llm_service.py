import torch
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration


class LLMService:
    def __init__(self, model_path=None, device=None):
        """
        初始化 LLMService

        model_path: 模型路径，默认使用 Qwen2-VL-2B-Instruct
        device: 使用设备，默认自动选择 CUDA 或 CPU
        """
        self.qwen_model_path = model_path or "/mnt/data/modelscope_cache/hub/Qwen/Qwen2-VL-2B-Instruct"
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        print(f"🧠 正在加载 Qwen2-VL 模型：{self.qwen_model_path} 到设备：{self.device}")

        try:
            # 加载多模态处理器
            self.processor = AutoProcessor.from_pretrained(self.qwen_model_path)

            # 加载模型
            self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                self.qwen_model_path,
                torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
            ).eval()

            print("✅ 模型加载成功！")

        except Exception as e:
            raise RuntimeError(f"❌ 加载模型失败: {e}")

    def generate_text(self, prompt: str, image=None, max_new_tokens=256):
        """
        生成文本

        prompt: 文本输入
        image: 可选，传入图像（PIL.Image 或 numpy）
        max_new_tokens: 最大生成长度
        """
        try:
            # 构造输入
            if image is not None:
                inputs = self.processor(
                    text=prompt,
                    images=image,
                    return_tensors="pt"
                ).to(self.device)
            else:
                inputs = self.processor(
                    text=prompt,
                    return_tensors="pt"
                ).to(self.device)

            # 推理生成
            output = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens
            )

            # 解码输出
            result = self.processor.batch_decode(output, skip_special_tokens=True)[0]
            return result.strip()

        except Exception as e:
            return f"⚠️ 生成文本时出错: {e}"

    def chat(self, prompt: str, image=None, max_new_tokens=256):
        """
        chat 方法，封装 generate_text
        """
        return self.generate_text(prompt, image=image, max_new_tokens=max_new_tokens)


# 独立测试脚本使用
if __name__ == "__main__":
    model_path = "/home/jiang/.cache/modelscope/hub/Qwen/Qwen2-VL-2B-Instruct"
    llm = LLMService(model_path)

    # 纯文本测试
    prompt = "你好，请介绍一下你自己。"
    response = llm.chat(prompt)
    print("🗣️ 模型输出：", response)

    # 图文测试（如果有 PIL.Image 可以传入）
    # from PIL import Image
    # img = Image.open("test.jpg")
    # response_img = llm.chat("请描述这张图片。", image=img)
    # print("🖼️ 模型输出：", response_img)




