#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import json
from datetime import datetime
from parsers.zsh_history_parser import parse_zsh_history
from parsers.safari_parser import parse_safari_history
from parsers.chrome_parser import parse_chrome_history
from utils.time_merger import merge_activities
from analysis.summarizer import summarize_activities

def parse_date(date_str):
    """将YYYYMMDD格式的日期字符串转换为datetime对象"""
    try:
        return datetime.strptime(date_str, '%Y%m%d')
    except ValueError:
        print(f"错误：日期格式应为YYYYMMDD，收到的是 '{date_str}'")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='解析并分析电脑操作记录')
    parser.add_argument('date', nargs='?', help='要处理的日期，格式为YYYYMMDD')
    parser.add_argument('--json', help='直接分析指定的JSON文件（跳过解析步骤）')
    parser.add_argument('--output', '-o', help='输出文件路径，默认为标准输出')
    args = parser.parse_args()
    
    # 如果提供了JSON文件路径，直接进行分析
    if args.json:
        return analyze_json_file(args.json, args.output)
    
    if not args.date:
        print("错误：请提供日期参数，格式为YYYYMMDD")
        sys.exit(1)
    
    # 解析日期参数
    target_date = parse_date(args.date)
    print(f"正在处理 {target_date.strftime('%Y-%m-%d')} 的操作记录...")
    
    # 解析各种历史记录
    zsh_activities = parse_zsh_history(target_date)
    print(f"找到 {len(zsh_activities)} 条终端命令记录")
    
    safari_activities = parse_safari_history(target_date)
    print(f"找到 {len(safari_activities)} 条Safari浏览记录")
    
    chrome_activities = parse_chrome_history(target_date)
    print(f"找到 {len(chrome_activities)} 条Chrome浏览记录")
    
    # 合并所有活动记录
    all_activities = merge_activities(zsh_activities, safari_activities, chrome_activities)
    print(f"总计 {len(all_activities)} 条活动记录")
    
    # 使用大模型分析总结
    summary = summarize_activities(all_activities)
    
    # 输出结果
    output_summary(summary, args.output)
    
    # TODO: 将结果记录到Google系统

def analyze_json_file(json_path, output_path=None):
    """分析已有的JSON文件"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"从 {json_path} 加载了 {len(data)} 条活动记录")
        
        # TODO: 调用大模型分析已有的JSON记录
        # 这里需要实现从JSON直接分析的功能
        
        print("暂不支持直接从JSON文件分析，此功能将在未来版本中实现")
        return 1
    
    except Exception as e:
        print(f"分析JSON文件时出错: {str(e)}")
        return 1

def output_summary(summary, output_path=None):
    """输出摘要结果"""
    # 格式化输出
    output = "\n===== 活动摘要 =====\n"
    output += summary.get("summary", "无摘要") + "\n\n"
    
    if "categories" in summary and summary["categories"]:
        output += "分类: " + ", ".join(summary["categories"]) + "\n"
    
    if "stats" in summary:
        output += "\n活动统计:\n"
        for activity_type, count in summary["stats"].items():
            if activity_type == "terminal":
                output += f"- 终端命令: {count}条\n"
            elif activity_type == "safari":
                output += f"- Safari浏览: {count}条\n"
            elif activity_type == "chrome":
                output += f"- Chrome浏览: {count}条\n"
    
    if "time_range" in summary:
        output += f"\n活动时间范围: {summary['time_range']}\n"
    
    if "output_file" in summary:
        output += f"\n详细记录已保存到: {summary['output_file']}\n"
    
    # 输出结果
    if output_path:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"摘要已保存到 {output_path}")
        except Exception as e:
            print(f"保存摘要时出错: {str(e)}")
            print(output)
    else:
        print(output)

if __name__ == '__main__':
    main() 