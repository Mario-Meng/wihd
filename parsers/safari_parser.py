#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import subprocess
from datetime import datetime
from utils.models import Activity, ActivityType

def parse_safari_history(target_date):
    """
    解析Safari的浏览历史记录
    
    Args:
        target_date (datetime): 目标日期
    
    Returns:
        list: 包含当天Safari浏览活动的列表
    """
    activities = []
    
    # 计算目标日期的边界时间字符串
    start_date_str = target_date.strftime("%Y-%m-%d 00:00:00")
    end_date_str = target_date.strftime("%Y-%m-%d 23:59:59")
    
    # Safari历史数据库路径
    safari_db_path = os.path.expanduser("~/Library/Safari/History.db")
    
    # 检查文件是否存在
    if not os.path.exists(safari_db_path):
        print(f"警告：Safari历史记录数据库不存在: {safari_db_path}")
        return activities
    
    # 由于权限问题，先复制数据库到临时位置
    temp_db_path = "/tmp/safari_history_temp.db"
    try:
        # 尝试直接复制
        subprocess.run(["cp", safari_db_path, temp_db_path], check=True)
    except subprocess.CalledProcessError:
        # 如果直接复制失败，输出更友好的提示
        print("\n访问Safari历史记录需要特殊权限")
        print("由于macOS的安全机制，需要授予终端访问浏览器历史数据的权限")
        print("请在系统偏好设置 -> 安全性与隐私 -> 隐私 -> 完全磁盘访问权限中添加终端应用")
        print("或者，您可以手动复制Safari历史文件:")
        print(f"sudo cp {safari_db_path} ~/Downloads/")
        print("然后更新代码以从下载目录读取文件\n")
        return activities
    
    # 查询历史记录
    try:
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT datetime(visit_time + 978307200, 'unixepoch', 'localtime') as visit_date, 
               url, 
               title 
        FROM history_visits 
        INNER JOIN history_items ON history_items.id = history_visits.history_item 
        WHERE visit_date BETWEEN ? AND ?
        ORDER BY visit_time DESC
        """
        
        cursor.execute(query, (start_date_str, end_date_str))
        results = cursor.fetchall()
        
        for visit_date_str, url, title in results:
            # 解析时间字符串为datetime对象
            visit_date = datetime.strptime(visit_date_str, "%Y-%m-%d %H:%M:%S")
            
            # 截取URL前100个字符
            truncated_url = url[:100] if url else url
            
            activity = Activity(
                timestamp=visit_date,
                activity_type=ActivityType.SAFARI,
                content=truncated_url,
                source="safari_history",
                title=title
            )
            activities.append(activity)
        
        conn.close()
        
        # 清理临时文件
        os.remove(temp_db_path)
        
    except Exception as e:
        print(f"解析Safari历史记录时出错: {str(e)}")
    
    # 按时间戳排序
    activities.sort(key=lambda x: x.timestamp)
    return activities

def test_parse_safari_history():
    """测试函数，用于调试"""
    # 测试当天的记录
    today = datetime.now()
    activities = parse_safari_history(today)
    
    print(f"今天找到 {len(activities)} 条Safari浏览记录:")
    for idx, activity in enumerate(activities[:10], 1):  # 只显示前10条
        print(f"{idx}. [{activity.timestamp.strftime('%H:%M:%S')}] {activity.title or '无标题'} - {activity.content}")
    
    if len(activities) > 10:
        print(f"... 以及其他 {len(activities) - 10} 条记录")

if __name__ == "__main__":
    # 直接运行此文件时测试功能
    test_parse_safari_history() 