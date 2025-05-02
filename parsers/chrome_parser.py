#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import subprocess
import shutil
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
    
    # Chrome历史数据库路径
    chrome_db_path = os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/History")
    
    # 检查文件是否存在
    if not os.path.exists(chrome_db_path):
        print(f"警告：Chrome历史记录数据库不存在: {chrome_db_path}")
        return activities
    
    # 由于Chrome可能正在使用数据库，先复制数据库到临时位置
    temp_db_path = "/tmp/chrome_history_temp.db"
    try:
        shutil.copy2(chrome_db_path, temp_db_path)
    except Exception as e:
        print("\n访问Chrome历史记录需要特殊权限")
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
            
            activity = Activity(
                timestamp=visit_date,
                activity_type=ActivityType.CHROME,
                content=url,
                source="chrome_history",
                title=title
            )
            activities.append(activity)
        
        conn.close()
        
        # 清理临时文件
        os.remove(temp_db_path)
        
    except Exception as e:
        print(f"解析Chrome历史记录时出错: {str(e)}")
    
    # 按时间戳排序
    activities.sort(key=lambda x: x.timestamp)
    return activities

def test_parse_chrome_history():
    """测试函数，用于调试"""
    # 测试当天的记录
    today = datetime.now()
    activities = parse_chrome_history(today)
    
    print(f"今天找到 {len(activities)} 条Chrome浏览记录:")
    for idx, activity in enumerate(activities[:10], 1):  # 只显示前10条
        print(f"{idx}. [{activity.timestamp.strftime('%H:%M:%S')}] {activity.title or '无标题'} - {activity.content[:50]}{'...' if len(activity.content) > 50 else ''}")
    
    if len(activities) > 10:
        print(f"... 以及其他 {len(activities) - 10} 条记录")

if __name__ == "__main__":
    # 直接运行此文件时测试功能
    test_parse_chrome_history() 