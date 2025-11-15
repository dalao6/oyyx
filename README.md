# oyyx

一个基于 Python 的 智能服饰识别与购物 模型系统。
该系统整合了语音识别 (ASR)、多模态视觉–语言模型 (VLM)、文本‑转语音 (TTS) 及图像检索模块，可实现用户通过摄像头识别衣物，并弹出相似商品信息。

## 功能特性

* 自动打开笔记本前置摄像头，对用户当前穿着或摆放的衣物进行识别。
* 利用多模态视觉语言模型 (VLM) 提取衣物特征，并在本地商品库中检索相似产品。
* 若识别成功，高置信度情况下弹出商品图片和详细信息窗口。
* 支持语音指令“我不要了”来关闭当前商品窗口并继续识别下一件。
* 支持“返回主页面”按钮，一键退出识别流程并返回初始 UI。
* 商品库来自 `data/product_images` & `data/product_specs`，你可自定义扩展商品图片与规格。

## 模型与路径

* VLM 模型：`/mnt/data/modelscope_cache/hub/HuggingFaceTB`
* ASR 模型：`/mnt/data/modelscope_cache/hub/xiaowangge/sherpa-onnx-sense-voice-small`
* TTS 模型：`/mnt/data/modelscope_cache/hub/pengzhendong/index=TTS`
* LLM 模型（可选增强）：`/mnt/data/modelscope_cache/hub/Qwen/Qwen2‑VL‑2B‑Instruct`

## 目录结构（核心部分）

```
oyyx/
├── DuoMotai/
│   ├── data/                # 存放商品图片、规格等数据  
│   ├── modules/             # 各项模块：ASR, TTS, vision, retrieval 等  
│   ├── gui/                 # 主界面与弹窗相关 UI 文件  
│   └── fin.py               # 主程序入口  
├── find_something/          # “识别相似物品购物”流程模块  
│   ├── camera_capture.py  
│   ├── vision_processor.py  
│   ├── voice_command.py  
│   ├── gui_display.py  
│   ├── controller.py  
│   └── main_find.py         # 流程入口  
└── README.md                # 项目说明文件  
```

## 快速开始

1. 克隆仓库：

   ```bash
   git clone https://github.com/dalao6/oyyx.git
   cd oyyx
   ```
2. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```
3. 根据你的模型存放路径，检查 `find_something/vision_processor.py`、`voice_command.py` 等模块中模型加载路径是否正确。
4. 启动识别流程：

   ```bash
   python3 find_something/main_find.py
   ```
5. 系统打开摄像头，开始识别流程。你可说“我不要了”关闭当前商品，也可点击 UI “返回主页面”退出流程。

## 使用说明

* **识别触发条件**：系统默认每 3 秒识别一次；当连续 3 次识别同一商品且置信度 ≥ 0.92 时弹出商品窗口。
* **语音交互**：识别窗口弹出后，你可说“我不要了”跳过当前商品；若说“停止”或“返回主页面”，则退出流程。
* **扩展商品库**：向 `DuoMotai/data/product_images/` 添加图片（如 `品牌_颜色_款式.jpg`），对应规格可在 `DuoMotai/data/product_specs/` 添加同名 JSON 文件，如 `{ "名称": "...", "价格": "...", "描述": "..." }`。
* **模型更换**：如需增强识别能力，可替换 VLM 模型为专门服饰识别模型，并在 `vision_processor.py` 中调整 *model_path*。

## 注意事项

* 确保摄像头驱动正常、网络环境稳定（如模型需要远程下载）。
* 若识别频次过快或误识别多，可适当提高置信度阈值（如 ≥0.95）或延长识别间隔。
* 对于商品库非常大的情况，建议提前生成商品 embedding 索引以加速匹配。

## 贡献 & 许可证

欢迎提交 issue 或 pull request 改进模型、识别逻辑或 UI 界面。
本项目采用 MIT 许可证，详见 LICENSE 文件。

---

