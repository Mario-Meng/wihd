# WIHD (What I Have Done)

这是一个电脑操作记录分析工具，可以帮助你整理、归档并分析你的日常电脑使用情况。

## 功能特点

- 解析zsh终端历史记录
- 解析Safari浏览历史记录
- 解析Chrome浏览历史记录
- 按时间顺序整合所有活动记录
- 使用AI进行活动分析和摘要生成
- 将活动记录保存为JSON文件

## 环境要求

- Python 3.7+
- macOS系统（针对Safari和zsh历史记录解析）

## 安装方法

1. 克隆项目到本地：
```bash
git clone <repository-url>
cd wihd
```

2. 安装依赖（如有需要）：
```bash
pip install -r requirements.txt  # 未来可能会添加
```

3. 配置zsh历史记录（**重要**）：
   
   为了确保zsh历史记录包含时间戳并能被正确解析，请在`~/.zprofile`文件中添加以下配置：
   
   ```bash
   # 历史记录设置
   HISTSIZE=1000000
   SAVEHIST=1000000
   setopt EXTENDED_HISTORY
   setopt SHARE_HISTORY        # 共享历史记录
   setopt INC_APPEND_HISTORY   # 增量添加历史记录
   ```
   
   然后重启终端或运行`source ~/.zprofile`使配置生效。

## 使用方法

### 基本用法

使用指定日期参数运行程序：

```bash
python main.py 20250503  # 分析2025年5月3日的操作记录
```

使用当天日期：

```bash
python main.py $(date +%Y%m%d)  # 分析今天的操作记录
```

### 文件权限设置

由于macOS的安全机制，访问浏览器历史记录需要特殊权限。有两种方法可以解决这个问题：

#### 方法一：授予终端完全磁盘访问权限

1. 打开"系统偏好设置" > "安全性与隐私" > "隐私" > "完全磁盘访问权限"
2. 点击左下角的锁图标并输入密码以进行更改
3. 点击"+"添加你的终端应用程序（Terminal或iTerm等）
4. 重启终端后，程序应该能够访问浏览器历史记录

#### 方法二：手动复制历史文件

如果不想授予终端完全磁盘访问权限，可以手动复制浏览器历史文件：

```bash
# 复制Safari历史文件
sudo cp ~/Library/Safari/History.db ~/Downloads/

# 复制Chrome历史文件
cp ~/Library/Application\ Support/Google/Chrome/Default/History ~/Downloads/
```

然后修改代码中的文件路径以从下载目录读取数据。

## 输出文件

程序会在`output`目录下生成带有时间戳的JSON文件，包含所有解析到的活动记录：

```
output/activities_YYYYMMDD_HHMMSS.json
```

## 项目结构

```
wihd/
├── main.py                   # 主入口程序
├── parsers/                  # 各类解析器
│   ├── __init__.py
│   ├── zsh_history_parser.py  # zsh历史记录解析
│   ├── safari_parser.py       # Safari历史记录解析
│   └── chrome_parser.py       # Chrome历史记录解析
├── utils/                    # 工具函数
│   ├── __init__.py
│   ├── models.py              # 数据模型定义
│   └── time_merger.py         # 时间合并工具
├── analysis/                 # 分析模块
│   ├── __init__.py
│   └── summarizer.py          # 活动总结生成器
└── output/                   # 输出目录
    └── activities_*.json      # 保存的活动记录
```

## 开发计划

- [ ] 添加更多浏览器的支持（Firefox等）
- [ ] 集成大模型API进行更详细分析
- [ ] 添加数据可视化功能
- [ ] 支持与Google日历/任务集成
- [ ] 添加Web界面，方便查看和管理活动记录
- [ ] 实现更智能的活动分类和标签 