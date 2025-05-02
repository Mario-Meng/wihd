#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def merge_activities(*activity_lists):
    """
    合并多个活动列表，按时间戳排序
    
    Args:
        *activity_lists: 可变参数，传入多个活动列表
    
    Returns:
        list: 合并后的活动列表，按时间排序
    """
    # 合并所有活动
    all_activities = []
    for activities in activity_lists:
        all_activities.extend(activities)
    
    # 按时间戳排序
    all_activities.sort(key=lambda x: x.timestamp)
    
    return all_activities 