# Real-ESRGAN 视频画质增强工具

基于 Real-ESRGAN 技术的视频画质增强工具，可将低分辨率视频提升到更高分辨率。
<img width="776" height="688" alt="捕获" src="https://github.com/user-attachments/assets/c2f082c1-e8c0-46df-b7e6-59352dc12973" />

## 功能特性

- 一键式视频画质增强
- 集成 Python 环境，无需额外安装
- 图形用户界面，操作简便
- 支持多种增强模型
- 优化了与各种媒体播放器的兼容性

## 系统要求

- Windows 7 及以上版本
- 至少 4GB 内存
- NVIDIA/AMD/Intel GPU（支持 Vulkan）

##快速开始

### 1. 启动程序

双击项目根目录下的 start.bat 文件启动程序，或右键选择"以管理员身份运行"。
clean.bat - 清理 tmp_frames 和 out_frames 文件夹的内容。

### 2. 使用主程序

程序启动后将打开图形界面：

1. 点击“浏览”按钮选择要增强的视频文件
2. 根据需要调整增强参数：
   - **增强模型**：选择合适的模型
     - `realesr-animevideov3`：适用于动漫视频
     - `realesrgan-x4plus`：适用于一般视频
     - `realesrgan-x4plus-anime`：适用于动漫图像
   - **缩放因子**：选择放大倍数（2x, 3x, 4x）
   - **输出格式**: 选择帧图像格式（jpg, png）
3. 点击"开始增强"按钮执行处理

## 处理流程

1. **提取帧**: 使用 ffmpeg 从视频中提取帧保存到[tmp_frames]文件夹
2. **增强帧**: 使用 Real-ESRGAN 增强帧，结果保存在[out_frames]文件夹
3. **合并视频**: 将增强后的帧合并为视频，保持原始帧率
4. **输出结果**: 增强后的视频保存在桌面，文件名格式为 `enhanced_原文件名_YYYYMMDD_HHMMSS.扩展名`

## 支持的视频格式

- MP4
- AVI
- MKV
- MOV
- WMV
- FLV
- WEBM

## 播放器兼容性

增强后的视频已针对主流播放器进行了优化：

- ✅ **PotPlayer** - 完全兼容
- ✅ **QQ播放器** - 兼容（已在最新版本中修复）
- ✅ **VLC Media Player** - 完全兼容
- ✅ **Windows Media Player** - 兼容

## 参数说明

### 增强模型

- **realesr-animevideov3**: 专为动漫视频优化的模型，提供最佳的动漫视频增强效果
- **realesrgan-x4plus**: 通用视频增强模型，适用于各种类型的视频
- **realesrgan-x4plus-anime**: 专门为动漫图像优化的模型

### 缩放因子

- **2**: 2倍超分辨率（推荐，处理速度快）
- **3**: 3倍超分辨率
- **4**: 4倍超分辨率（最高质量，处理时间较长）

### 输出格式

- **jpg**: JPEG格式，文件较小
- **png**: PNG格式，无损压缩，文件较大

## 文件结构说明

```
项目根目录/
├── ffmpeg.exe              # 视频处理工具
├── realesrgan-ncnn-vulkan.exe  # Real-ESRGAN推理工具
├── video_enhancer.py       # 主程序
├── start.bat               # 启动脚本
├── clean.bat               # 清理脚本
├── requirements.txt        # Python依赖
├── README.md               # 英文项目说明
├── README_zh.md            # 中文项目说明
├── USAGE.md                # 使用说明
├── models/                 # 增强模型文件
│   ├── *.bin
│   └── *.param
├── python/                 # 集成的Python环境
├── tmp_frames/             # 临时帧文件夹（自动生成）
└── out_frames/             # 增强后的帧文件夹（自动生成）
```

## 注意事项

1. **处理时间**: 视频增强是一个计算密集型任务，处理时间取决于：
   - 视频长度和分辨率
   - 选择的缩放因子
   - 计算机硬件性能

2. **存储空间**: 确保有足够的磁盘空间，处理过程中会生成大量临时文件

3. **内存使用**: 处理高分辨率视频时可能需要大量内存

4. **GPU加速**: 工具会自动使用GPU加速，确保安装了最新的显卡驱动

## 故障排除

### 常见问题

1. **程序无法启动**
   - 确保所有文件都在同一目录下
   - 检查是否有杀毒软件阻止程序运行
   - 以管理员身份运行程序

2. **增强效果不理想**
   - 尝试不同的增强模型
   - 调整缩放因子
   - 对于动漫视频，使用`realesr-animevideov3`模型

3. **处理过程中出错**
   - 检查视频文件是否损坏
   - 确保有足够的磁盘空间
   - 关闭其他占用大量资源的程序

## 技术支持

如果遇到问题，请提供以下信息以便更好地帮助您：

1. 错误信息截图
2. 操作系统版本
3. 视频文件格式和大小
4. 计算机硬件配置（CPU、GPU、内存）

## 版权声明

本工具基于以下开源项目：

- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)
- [ffmpeg](https://ffmpeg.org/)
- [Python](https://www.python.org/)

本项目采用 MIT 许可证，详情请见 [LICENSE](LICENSE) 文件。
