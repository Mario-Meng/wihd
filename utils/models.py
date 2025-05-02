#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional


class ActivityType(Enum):
    """活动类型枚举"""
    TERMINAL = "terminal"  # 终端命令
    SAFARI = "safari"      # Safari浏览记录
    CHROME = "chrome"      # Chrome浏览记录


@dataclass
class Activity:
    """活动记录类"""
    timestamp: datetime                    # 活动发生的时间
    activity_type: ActivityType            # 活动类型
    content: str                           # 活动内容（命令或URL）
    source: str                            # 数据来源
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外元数据
    title: Optional[str] = None            # 网页标题（对于浏览记录）
    
    def __str__(self):
        """字符串表示"""
        if self.activity_type in [ActivityType.SAFARI, ActivityType.CHROME] and self.title:
            return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] [{self.activity_type.value}] {self.title} - {self.content}"
        else:
            return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] [{self.activity_type.value}] {self.content}" 