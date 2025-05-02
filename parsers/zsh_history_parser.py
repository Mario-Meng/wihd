#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from datetime import datetime, timedelta
from utils.models import Activity, ActivityType

def parse_zsh_history(target_date):
    """
    解析~/.zsh_history文件，提取指定日期的命令记录
    
    Args:
        target_date (datetime): 目标日期
    
    Returns:
        list: 包含当天命令活动的列表
    """
    # 计算目标日期的开始和结束时间戳
    start_timestamp = int(datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0).timestamp())
    end_timestamp = int(datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59).timestamp())
    
    zsh_history_path = os.path.expanduser("~/.zsh_history")
    activities = []
    
    if not os.path.exists(zsh_history_path):
        print(f"警告: zsh历史记录文件 {zsh_history_path} 不存在")
        return activities
    
    # zsh_history格式示例: ": 1746205574:0;cd ~/Downloads/"
    # 格式为: ": [时间戳]:[持续时间];[命令]"
    line_pattern = re.compile(r'^: (\d+):(\d+);(.*)$')
    
    try:
        with open(zsh_history_path, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                line = line.strip()
                match = line_pattern.match(line)
                
                if not match:
                    continue
                
                timestamp, duration, command = match.groups()
                timestamp = int(timestamp)
                
                # 检查是否在目标日期范围内
                if start_timestamp <= timestamp <= end_timestamp:
                    activity_time = datetime.fromtimestamp(timestamp)
                    activity = Activity(
                        timestamp=activity_time,
                        activity_type=ActivityType.TERMINAL,
                        content=command,
                        source="zsh_history",
                        metadata={"duration": duration}
                    )
                    activities.append(activity)
    except Exception as e:
        print(f"解析zsh历史记录时出错: {str(e)}")
    
    # 按时间戳排序
    activities.sort(key=lambda x: x.timestamp)
    return activities

def test_parse_zsh_history():
    """测试函数，用于调试"""
    # 测试当天的记录
    today = datetime.now()
    activities = parse_zsh_history(today)
    
    print(f"今天找到 {len(activities)} 条终端命令记录:")
    for idx, activity in enumerate(activities[:10], 1):  # 只显示前10条
        print(f"{idx}. [{activity.timestamp.strftime('%H:%M:%S')}] {activity.content[:80]}{'...' if len(activity.content) > 80 else ''}")
    
    if len(activities) > 10:
        print(f"... 以及其他 {len(activities) - 10} 条记录")

if __name__ == "__main__":
    # 直接运行此文件时测试功能
    test_parse_zsh_history() 