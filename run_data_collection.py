#!/usr/bin/env python3
"""
数据采集和填充脚本
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_collection.utils.data_integration import DataIntegrationManager

def main():
    """主函数"""
    print("开始数据采集和填充...")
    
    try:
        # 创建数据整合管理器
        manager = DataIntegrationManager()
        
        # 整合数据
        print("整合数据中...")
        integrated_data = manager.integrate_data()
        
        # 导出到StrategyKG
        print("导出到StrategyKG...")
        strategy_kg_data = manager.export_to_strategy_kg()
        
        print("数据采集和填充完成！")
        print(f"整合后数据: {integrated_data.get('metadata', {})}")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
