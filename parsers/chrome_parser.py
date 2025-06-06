#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import subprocess
import shutil
import glob
from datetime import datetime
from utils.models import Activity, ActivityType

def parse_chrome_history(target_date):
    """
    解析Chrome的浏览历史记录
    
    Args:
        target_date (datetime): 目标日期
    
    Returns:
        list: 包含当天Chrome浏览活动的列表
    """
    activities = []
    
    # 计算目标日期的Unix时间戳（微秒级）
    # Chrome使用的是从1601年1月1日开始的微秒数
    # 首先计算目标日期的边界时间
    start_date = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
    end_date = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)
    
    # Chrome基础目录
    chrome_base_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome")
    
    # 获取所有可能的配置文件目录
    profile_dirs = find_chrome_profiles(chrome_base_dir)
    
    if not profile_dirs:
        print("未找到Chrome配置文件目录")
        return activities
    
    # 依次处理每个配置文件
    for profile_name, profile_path in profile_dirs.items():
        # Chrome历史数据库路径
        chrome_db_path = os.path.join(profile_path, "History")
        
        # 检查文件是否存在
        if not os.path.exists(chrome_db_path):
            print(f"警告：Chrome历史记录数据库不存在: {chrome_db_path}")
            continue
        
        print(f"正在处理Chrome配置文件 '{profile_name}' 的历史记录...")
        
        # 读取此配置文件的历史记录
        profile_activities = parse_chrome_profile_history(chrome_db_path, start_date, end_date, profile_name)
        activities.extend(profile_activities)
    
    # 按时间戳排序
    activities.sort(key=lambda x: x.timestamp)
    return activities

def find_chrome_profiles(chrome_base_dir):
    """
    查找所有Chrome配置文件目录
    
    Args:
        chrome_base_dir (str): Chrome基础目录
    
    Returns:
        dict: 配置文件名到路径的映射
    """
    profiles = {}
    
    # 检查Default配置文件
    default_path = os.path.join(chrome_base_dir, "Default")
    if os.path.exists(default_path) and os.path.isdir(default_path):
        profiles["Default"] = default_path
    
    # 检查其他Profile配置文件
    profile_pattern = os.path.join(chrome_base_dir, "Profile *")
    for profile_dir in glob.glob(profile_pattern):
        if os.path.isdir(profile_dir):
            profile_name = os.path.basename(profile_dir)
            profiles[profile_name] = profile_dir
    
    return profiles

def parse_chrome_profile_history(chrome_db_path, start_date, end_date, profile_name):
    """
    解析单个Chrome配置文件的历史记录
    
    Args:
        chrome_db_path (str): Chrome历史数据库路径
        start_date (datetime): 开始日期
        end_date (datetime): 结束日期
        profile_name (str): 配置文件名称
    
    Returns:
        list: 包含当天Chrome浏览活动的列表
    """
    activities = []
    
    # 由于Chrome可能正在使用数据库，先复制数据库到临时位置
    temp_db_path = f"/tmp/chrome_history_{profile_name}_temp.db"
    try:
        shutil.copy2(chrome_db_path, temp_db_path)
    except Exception as e:
        print(f"\n访问Chrome配置文件 '{profile_name}' 的历史记录需要特殊权限")
        print("由于macOS的安全机制，需要授予终端访问浏览器历史数据的权限")
        print("请在系统偏好设置 -> 安全性与隐私 -> 隐私 -> 完全磁盘访问权限中添加终端应用")
        print("或者，您可以手动复制Chrome历史文件:")
        print(f"cp \"{chrome_db_path}\" ~/Downloads/")
        print("然后更新代码以从下载目录读取文件\n")
        return activities
    
    # 查询历史记录
    try:
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # Chrome中的时间是从1601年1月1日开始的微秒数
        # 转换为Unix时间戳需要减去11644473600000000（1601年到1970年的微秒数）再除以1000000
        query = """
        SELECT datetime((last_visit_time/1000000)-11644473600, 'unixepoch', 'localtime') as visit_date,
               url,
               title
        FROM urls
        WHERE datetime((last_visit_time/1000000)-11644473600, 'unixepoch', 'localtime') BETWEEN ? AND ?
        ORDER BY last_visit_time DESC
        """
        
        cursor.execute(query, (start_date.strftime("%Y-%m-%d %H:%M:%S"), 
                              end_date.strftime("%Y-%m-%d %H:%M:%S")))
        results = cursor.fetchall()
        
        for visit_date_str, url, title in results:
            # 解析时间字符串为datetime对象
            visit_date = datetime.strptime(visit_date_str, "%Y-%m-%d %H:%M:%S")
            
            # 截取URL前100个字符
            truncated_url = url[:100] if url else url
            
            activity = Activity(
                timestamp=visit_date,
                activity_type=ActivityType.CHROME,
                content=truncated_url,
                source=f"chrome_history_{profile_name}",
                title=title,
                metadata={"profile": profile_name}
            )
            activities.append(activity)
        
        conn.close()
        
        # 清理临时文件
        os.remove(temp_db_path)
        
        print(f"从Chrome配置文件 '{profile_name}' 中找到 {len(activities)} 条浏览记录")
        
    except Exception as e:
        print(f"解析Chrome配置文件 '{profile_name}' 的历史记录时出错: {str(e)}")
    
    return activities

def test_parse_chrome_history():
    """测试函数，用于调试"""
    # 测试当天的记录
    today = datetime.now()
    activities = parse_chrome_history(today)
    
    print(f"\n今天找到总计 {len(activities)} 条Chrome浏览记录:")
    
    # 按配置文件分组显示
    profiles = {}
    for activity in activities:
        profile = activity.metadata.get("profile", "未知")
        if profile not in profiles:
            profiles[profile] = []
        profiles[profile].append(activity)
    
    for profile, acts in profiles.items():
        print(f"\n配置文件 '{profile}' 中有 {len(acts)} 条记录:")
        for idx, activity in enumerate(acts[:5], 1):  # 只显示前5条
            print(f"{idx}. [{activity.timestamp.strftime('%H:%M:%S')}] {activity.title or '无标题'} - {activity.content}")
        
        if len(acts) > 5:
            print(f"... 以及其他 {len(acts) - 5} 条记录")

if __name__ == "__main__":
    # 直接运行此文件时测试功能
    test_parse_chrome_history() 