#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime
from typing import List, Dict, Any

# 这里将来可以替换为实际的大模型API调用
# 目前使用简单的模拟功能

def summarize_activities(activities):
    """
    使用大模型分析和总结活动记录
    
    Args:
        activities (list): 活动记录列表
    
    Returns:
        dict: 包含总结和分类的字典
    """
    if not activities:
        return {"summary": "没有找到活动记录。", "categories": []}
    
    # 将活动转换为可序列化的格式
    activity_records = []
    for activity in activities:
        record = {
            "timestamp": activity.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "type": activity.activity_type.value,
            "content": activity.content,
            "source": activity.source
        }
        
        if activity.title:
            record["title"] = activity.title
            
        activity_records.append(record)
    
    # 保存活动记录为JSON以便调试
    output_file = save_activities_to_json(activity_records)
    
    # TODO: 在这里集成实际的大模型API
    # 调用示例:
    # summary = call_llm_api_for_summary(activity_records)
    
    # 目前返回一个简单的总结
    summary = generate_mock_summary(activities)
    
    # 将输出文件路径添加到结果中
    summary["output_file"] = output_file
    
    return summary

def save_activities_to_json(activity_records):
    """
    保存活动记录为JSON文件，便于调试
    
    Args:
        activity_records (list): 活动记录列表
        
    Returns:
        str: 保存的文件路径
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "output"
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"activities_{timestamp}.json")
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(activity_records, f, ensure_ascii=False, indent=2)
    
    print(f"活动记录已保存到 {output_file}")
    return output_file

def call_llm_api_for_summary(activity_records):
    """
    调用大语言模型API进行分析和总结
    
    Args:
        activity_records (list): 活动记录列表
        
    Returns:
        dict: 包含总结和分类的字典
    """
    # 这里是示例代码，展示如何调用大模型API
    # 实际使用时需要替换为真实的API调用
    
    try:
        # 构建提示词
        prompt = create_llm_prompt(activity_records)
        
        # API调用示例 (需要替换为实际的API)
        # response = openai.ChatCompletion.create(
        #     model="gpt-4",
        #     messages=[
        #         {"role": "system", "content": "你是一个专业的数据分析师，擅长总结用户的电脑使用行为。"},
        #         {"role": "user", "content": prompt}
        #     ],
        #     temperature=0.7,
        # )
        # 
        # summary_text = response.choices[0].message['content']
        
        # 这里应该解析API返回的结果
        # 将文本格式的总结转换为结构化数据
        # return parse_llm_response(summary_text)
        
        # 目前返回一个模拟的结果
        return generate_mock_summary(activity_records)
        
    except Exception as e:
        print(f"调用大模型API时出错: {str(e)}")
        # 如果API调用失败，返回一个简单的总结
        return generate_mock_summary(activity_records)

def create_llm_prompt(activity_records):
    """创建发送给大模型的提示词"""
    # 计算活动的基本统计信息
    activities_by_type = {}
    for record in activity_records:
        activity_type = record["type"]
        activities_by_type[activity_type] = activities_by_type.get(activity_type, 0) + 1
    
    # 构建提示词
    prompt = f"""我有一天的电脑活动记录，包含以下内容：
- {activities_by_type.get('terminal', 0)} 条终端命令
- {activities_by_type.get('safari', 0)} 条Safari浏览记录
- {activities_by_type.get('chrome', 0)} 条Chrome浏览记录

以下是部分活动记录（按时间顺序）：

"""
    
    # 添加一些示例活动记录
    max_samples = min(10, len(activity_records))
    for i in range(max_samples):
        record = activity_records[i]
        timestamp = record["timestamp"]
        activity_type = record["type"]
        content = record["content"]
        title = record.get("title", "")
        
        if activity_type in ["safari", "chrome"] and title:
            prompt += f"{timestamp} [{activity_type}] {title} - {content[:50]}...\n"
        else:
            prompt += f"{timestamp} [{activity_type}] {content[:100]}...\n"
    
    prompt += f"\n请分析这些活动记录，并提供以下内容：\n"
    prompt += f"1. 一段总结，描述我这一天的主要活动和使用电脑的目的\n"
    prompt += f"2. 将活动分类为不同的主题或项目\n"
    prompt += f"3. 识别我花费最多时间的活动类型\n"
    prompt += f"4. 提出改进我工作效率的建议\n"
    
    return prompt

def generate_mock_summary(activities):
    """生成模拟的总结（未来会替换为大模型调用）"""
    total_count = len(activities)
    
    # 计算各类型活动的数量
    type_counts = {}
    for activity in activities:
        activity_type = activity.activity_type.value
        type_counts[activity_type] = type_counts.get(activity_type, 0) + 1
    
    # 模拟生成分类标签
    categories = []
    
    if type_counts.get("terminal", 0) > 0:
        categories.append("命令行操作")
    
    if type_counts.get("safari", 0) > 0 or type_counts.get("chrome", 0) > 0:
        categories.append("网页浏览")
    
    # 生成时间范围
    if activities:
        start_time = min(activities, key=lambda x: x.timestamp).timestamp
        end_time = max(activities, key=lambda x: x.timestamp).timestamp
        time_range = f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
    else:
        time_range = "无数据"
    
    # 生成摘要文本
    summary = f"今天总共记录了{total_count}个活动，活动时间范围：{time_range}。"
    
    for activity_type, count in type_counts.items():
        if activity_type == "terminal":
            summary += f"执行了{count}条终端命令，"
        elif activity_type == "safari":
            summary += f"在Safari浏览器中访问了{count}个网页，"
        elif activity_type == "chrome":
            summary += f"在Chrome浏览器中访问了{count}个网页，"
    
    # 移除最后的逗号和空格
    summary = summary.rstrip(", ") + "。"
    
    # 添加提示
    summary += "\n\n注意：这是模拟的总结，未来将由大模型生成更详细的分析。"
    
    return {
        "summary": summary,
        "categories": categories,
        "stats": type_counts,
        "time_range": time_range
    }

def test_summarizer():
    """测试函数"""
    from utils.models import Activity, ActivityType
    
    # 创建一些测试活动
    activities = [
        Activity(
            timestamp=datetime.now(),
            activity_type=ActivityType.TERMINAL,
            content="ls -la",
            source="zsh_history"
        ),
        Activity(
            timestamp=datetime.now(),
            activity_type=ActivityType.SAFARI,
            content="https://www.google.com",
            source="safari_history",
            title="Google"
        )
    ]
    
    summary = summarize_activities(activities)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    test_summarizer() 