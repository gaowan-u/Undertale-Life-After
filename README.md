# 《传说之下：劫后余生》(Undertale: Survival After Disaster)

![游戏封面](images/background_5.jpg)

## 🎮 项目介绍
《传说之下：劫后余生》是一款基于 Toby Fox 的经典游戏《Undertale》世界观开发的同人游戏。游戏延续了原作独特的战斗系统和叙事风格，讲述了一个全新的地下世界冒险故事。

**核心特点**：
- 原汁原味的 Undertale 风格战斗系统
- 全新的故事情节与角色设定
- 复古像素美术风格 + 原创音乐
- 丰富的道德选择影响剧情走向

## ⚙️ 运行环境
- **平台**: Android
- **开发框架**: Pygame
- **必需组件**:
  - Termux
  - Termux-X11
  - Python 3.8+
- **推荐设备**: Android 9.0 及以上版本

## 📥 安装指南

### 1. 安装必要组件
```bash
# 更新包管理器
pkg update && pkg upgrade

# 安装基础组件
pkg install python git wget ffmpeg

# 安装X11支持
pkg install x11-repo
pkg install termux-x11-nightly
```

### 2. 安装Pygame依赖
```bash
# 安装编译依赖
pkg install make clang python

# 安装Pygame
pip install pygame
```

### 3. 获取游戏源码
```bash
git clone https://github.com/gaowan-u/Undertale-Life-After.git
cd Undertale-Life-After
```

## 🚀 运行游戏
```bash
# 启动Termux-X11服务
termux-x11 &

# 运行游戏
python main.py
```

## 📂 项目结构（实际结构）
```
.
├── README.md           # 项目说明文档
├── audios/             # 游戏音频文件
│   ├── begin.ogg       # 开始音乐
│   └── test.ogg        # 测试音乐
├── fonts/              # 字体文件
│   └── SourceHanSansSC-Regular-2.otf  # 思源黑体
├── images/             # 游戏图片资源
│   ├── background_1.png # 背景图1
│   ├── background_2.png # 背景图2
│   ├── background_3.png # 背景图3
│   └── background_4.png # 背景图4
├── main.py             # 游戏主程序
└── videos/             # 游戏视频文件
    └── begin.mp4       # 开场视频
```

## 🛠️ 开发指南
1. **资源规范**：
   - 图片：PNG 格式，建议尺寸 1920x1080
   - 音频：OGG 格式，44.1kHz
   - 视频：MP4 格式，H.264编码

2. **添加新资源**：
   - 将图片放入 `images/` 目录
   - 将音频放入 `audios/` 目录
   - 将视频放入 `videos/` 目录

## 📜 许可证
本项目采用 [MIT 许可证](LICENSE)，允许自由使用和修改代码，但请遵守：
- 不得用于商业目的
- 需注明原始项目来源
- 保留版权声明

---

> **温馨提示**：游戏仍在开发中，欢迎贡献代码！  
> 遇到问题？请提交 [Issue](https://github.com/gaowan-u/Undertale-Life-After/issues)