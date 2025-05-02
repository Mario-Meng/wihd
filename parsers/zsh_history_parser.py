#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
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
    
    # 尝试使用不同的格式解析zsh_history
    entries = parse_zsh_history_file(zsh_history_path)
    
    # 过滤出目标日期的条目
    for entry in entries:
        if 'timestamp' in entry and start_timestamp <= entry['timestamp'] <= end_timestamp:
            activity = Activity(
                timestamp=entry['time'],
                activity_type=ActivityType.TERMINAL,
                content=entry['command'],
                source="zsh_history",
                metadata=entry.get('metadata', {})
            )
            activities.append(activity)
    
    # 按时间戳排序
    activities.sort(key=lambda x: x.timestamp)
    return activities

def parse_zsh_history_file(file_path):
    """
    尝试使用多种方式解析zsh_history文件
    
    Args:
        file_path (str): zsh_history文件路径
    
    Returns:
        list: 解析出的历史记录条目
    """
    entries = []
    
    try:
        # 获取文件修改时间作为回退方案
        file_mtime = os.path.getmtime(file_path)
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
        
        # 处理标准格式的行
        standard_entries = []
        for line in lines:
            # 标准格式: ": [时间戳]:[持续时间];[命令]"
            match = re.match(r'^: (\d+):(\d+);(.*)$', line.strip())
            if match:
                timestamp, duration, command = match.groups()
                timestamp = int(timestamp)
                
                entry = {
                    'timestamp': timestamp,
                    'time': datetime.fromtimestamp(timestamp),
                    'command': command,
                    'metadata': {'duration': duration}
                }
                standard_entries.append(entry)
        
        # 如果找到标准格式的条目，直接返回它们
        if standard_entries:
            return standard_entries
            
        # 否则，处理非标准格式
        print("未找到标准格式的zsh_history条目，尝试使用估计时间...")
        print("请确保在~/.zprofile中添加以下设置以启用时间戳记录：")
        print("  HISTSIZE=1000000")
        print("  SAVEHIST=1000000")
        print("  setopt EXTENDED_HISTORY")
        print("  setopt SHARE_HISTORY")
        print("  setopt INC_APPEND_HISTORY")
        
        return parse_nonstandard_format(lines, file_mtime)
    
    except Exception as e:
        print(f"解析zsh历史记录时出错: {str(e)}")
        return []

def parse_nonstandard_format(lines, file_mtime=None):
    """
    解析非标准格式的zsh_history
    
    为每条命令分配一个估计的时间戳
    """
    entries = []
    
    if not file_mtime:
        file_mtime = time.time()
    
    # 估计每条命令的时间间隔（秒）
    interval = 60  # 假设平均每分钟执行一条命令
    
    # 从文件修改时间开始，向前推算
    current_timestamp = file_mtime
    
    for line in reversed(lines):  # 从最新的命令开始
        line = line.strip()
        if not line:
            continue
        
        # 跳过明显不是命令的行
        if line.startswith('{') and ('"choices":' in line or '"messages":' in line):
            continue
        
        current_timestamp -= interval
        
        entry = {
            'timestamp': int(current_timestamp),
            'time': datetime.fromtimestamp(current_timestamp),
            'command': line,
            'metadata': {'estimated': True}
        }
        entries.append(entry)
    
    # 反转列表，使其按时间顺序排列
    entries.reverse()
    
    return entries

def get_nearby_history_entries(target_date, days_before=3, days_after=1):
    """
    获取指定日期附近几天的历史记录，用于调试
    
    Args:
        target_date (datetime): 目标日期
        days_before (int): 向前查询的天数
        days_after (int): 向后查询的天数
    
    Returns:
        dict: 以日期字符串为键，命令列表为值的字典
    """
    result = {}
    
    # 遍历目标日期前后的日期
    for day_offset in range(-days_before, days_after+1):
        date = target_date + timedelta(days=day_offset)
        date_str = date.strftime('%Y-%m-%d')
        
        # 获取该日期的活动
        activities = parse_zsh_history(date)
        if activities:
            result[date_str] = activities
    
    return result

def test_parse_zsh_history(date_str=None, show_nearby=False):
    """
    测试函数，用于调试
    
    Args:
        date_str (str, optional): 日期字符串，格式为YYYYMMDD。如果不提供，则使用当天日期。
        show_nearby (bool): 是否显示附近日期的历史记录
    """
    # 如果提供了日期字符串，解析它；否则使用当天日期
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            print(f"错误：日期格式应为YYYYMMDD，收到的是 '{date_str}'")
            return
    else:
        target_date = datetime.now()
    
    print(f"正在解析 {target_date.strftime('%Y-%m-%d')} 的zsh历史记录...")
    
    # 打印日期范围的Unix时间戳，便于调试
    start_timestamp = int(datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0).timestamp())
    end_timestamp = int(datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59).timestamp())
    print(f"时间戳范围: {start_timestamp} - {end_timestamp}")
    print(f"对应时间: {datetime.fromtimestamp(start_timestamp)} - {datetime.fromtimestamp(end_timestamp)}")
    
    activities = parse_zsh_history(target_date)
    
    print(f"找到 {len(activities)} 条终端命令记录:")
    for idx, activity in enumerate(activities[:20], 1):  # 显示前20条
        estimated = "(估计时间)" if activity.metadata.get('estimated', False) else ""
        print(f"{idx}. [{activity.timestamp.strftime('%H:%M:%S')}]{estimated} {activity.content[:80]}{'...' if len(activity.content) > 80 else ''}")
    
    if len(activities) > 20:
        print(f"... 以及其他 {len(activities) - 20} 条记录")
    
    # 如果需要显示附近日期的历史记录
    if show_nearby and not activities:
        print("\n未找到当天记录，正在查询附近日期的历史记录...")
        nearby_activities = get_nearby_history_entries(target_date)
        
        if nearby_activities:
            print("\n附近日期的历史记录:")
            for date_str, acts in sorted(nearby_activities.items()):
                print(f"\n{date_str} 有 {len(acts)} 条记录:")
                for idx, activity in enumerate(acts[:5], 1):  # 每天只显示5条
                    estimated = "(估计时间)" if activity.metadata.get('estimated', False) else ""
                    print(f"  {idx}. [{activity.timestamp.strftime('%H:%M:%S')}]{estimated} {activity.content[:80]}{'...' if len(activity.content) > 80 else ''}")
                if len(acts) > 5:
                    print(f"  ... 以及其他 {len(acts) - 5} 条记录")
        else:
            print("附近日期也没有找到历史记录。")
    
    return activities

def dump_raw_history():
    """
    显示原始zsh_history文件内容进行调试
    """
    zsh_history_path = os.path.expanduser("~/.zsh_history")
    
    if not os.path.exists(zsh_history_path):
        print(f"警告: zsh历史记录文件 {zsh_history_path} 不存在")
        return
    
    print(f"zsh_history文件修改时间: {datetime.fromtimestamp(os.path.getmtime(zsh_history_path))}")
    print(f"zsh_history文件大小: {os.path.getsize(zsh_history_path)} 字节")
    
    try:
        with open(zsh_history_path, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
            
        print(f"总行数: {len(lines)}")
        print("\n前10行内容:")
        for i, line in enumerate(lines[:10]):
            print(f"{i+1}: {line.strip()}")
            
        print("\n后10行内容:")
        for i, line in enumerate(lines[-10:]):
            print(f"{len(lines)-10+i+1}: {line.strip()}")
    
    except Exception as e:
        print(f"读取zsh历史记录时出错: {str(e)}")

if __name__ == "__main__":
    # 直接运行此文件时测试功能
    if len(sys.argv) > 1:
        if sys.argv[1] == "--dump":
            # 显示原始历史文件内容
            dump_raw_history()
        elif sys.argv[1] == "--last":
            # 显示最近的历史命令
            count = 20
            if len(sys.argv) > 2 and sys.argv[2].isdigit():
                count = int(sys.argv[2])
            
            # 获取历史记录
            zsh_history_path = os.path.expanduser("~/.zsh_history")
            entries = parse_zsh_history_file(zsh_history_path)
            
            # 按时间戳排序
            entries.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            
            print(f"显示最近 {count} 条历史命令:")
            for idx, entry in enumerate(entries[:count], 1):
                time_str = entry['time'].strftime('%Y-%m-%d %H:%M:%S')
                estimated = "(估计时间)" if entry.get('metadata', {}).get('estimated', False) else ""
                print(f"{idx}. [{time_str}]{estimated} {entry['command'][:80]}{'...' if len(entry['command']) > 80 else ''}")
                
        elif sys.argv[1] == "--nearby":
            # 使用当天日期但显示附近日期的历史记录
            if len(sys.argv) > 2:
                test_parse_zsh_history(sys.argv[2], show_nearby=True)
            else:
                test_parse_zsh_history(show_nearby=True)
        else:
            # 正常模式，使用提供的日期
            test_parse_zsh_history(sys.argv[1])
    else:
        test_parse_zsh_history() 