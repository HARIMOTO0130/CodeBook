#!/usr/bin/env python3
"""
执行所有数据源的采集
"""

import os
import sys
import time
import random

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def retry(func, max_attempts=3, delay=2):
    """重试装饰器"""
    def wrapper(*args, **kwargs):
        attempts = 0
        while attempts < max_attempts:
            try:
                result = func(*args, **kwargs)
                if result:
                    return result
                else:
                    attempts += 1
                    if attempts >= max_attempts:
                        print(f"{func.__name__} 未返回有效结果，已达到最大重试次数")
                        return None
                    wait_time = delay * (2 ** attempts) + random.uniform(0, 1)
                    print(f"{func.__name__} 未返回有效结果，{wait_time:.2f}秒后重试 ({attempts}/{max_attempts})")
                    time.sleep(wait_time)
            except Exception as e:
                attempts += 1
                if attempts >= max_attempts:
                    print(f"{func.__name__} 失败，已达到最大重试次数: {e}")
                    return None
                wait_time = delay * (2 ** attempts) + random.uniform(0, 1)
                print(f"{func.__name__} 失败，{wait_time:.2f}秒后重试 ({attempts}/{max_attempts}): {e}")
                time.sleep(wait_time)
    return wrapper


@retry
def collect_mooccube():
    """采集MOOCCube数据"""
    from data_collection.mooccube.collector import MOOCCubeCollector
    collector = MOOCCubeCollector()
    return collector.collect_all()


@retry
def collect_wikidata():
    """采集Wikidata数据"""
    from data_collection.wikidata.collector import WikidataCollector
    collector = WikidataCollector()
    return collector.collect_all()


@retry
def collect_dbpedia():
    """采集DBpedia数据"""
    from data_collection.dbpedia.collector import DBpediaCollector
    collector = DBpediaCollector()
    return collector.collect_all()


@retry
def collect_education_platforms():
    """采集在线教育平台数据"""
    from data_collection.education_platforms.collector import EducationPlatformCollector
    collector = EducationPlatformCollector()
    return collector.collect_all()


@retry
def collect_textbooks():
    """采集教材与文档数据"""
    from data_collection.textbooks.spiders import run_spiders
    run_spiders()
    return "教材与文档采集完成"


def main():
    """主函数"""
    print("开始执行所有数据源的采集...")
    print("=" * 60)
    
    # 1. 采集MOOCCube数据
    print("\n1. 采集MOOCCube数据")
    mooccube_data = collect_mooccube()
    if mooccube_data:
        print("✓ MOOCCube采集成功")
    time.sleep(random.uniform(1, 3))  # 随机延迟避免请求过于频繁
    
    # 2. 采集Wikidata数据
    print("\n2. 采集Wikidata数据")
    wikidata_data = collect_wikidata()
    if wikidata_data:
        print("✓ Wikidata采集成功")
    time.sleep(random.uniform(1, 3))  # 随机延迟避免请求过于频繁
    
    # 3. 采集DBpedia数据
    print("\n3. 采集DBpedia数据")
    dbpedia_data = collect_dbpedia()
    if dbpedia_data:
        print("✓ DBpedia采集成功")
    time.sleep(random.uniform(1, 3))  # 随机延迟避免请求过于频繁
    
    # 4. 采集在线教育平台数据
    print("\n4. 采集在线教育平台数据")
    education_data = collect_education_platforms()
    if education_data:
        print("✓ 教育平台采集成功")
    time.sleep(random.uniform(1, 3))  # 随机延迟避免请求过于频繁
    
    # 5. 采集教材与文档数据
    print("\n5. 采集教材与文档数据")
    textbooks_data = collect_textbooks()
    if textbooks_data:
        print("✓ 教材与文档采集成功")
    time.sleep(random.uniform(1, 3))  # 随机延迟避免请求过于频繁
    
    # 6. 整合所有数据
    print("\n6. 整合所有数据")
    try:
        from data_collection.utils.data_integration import DataIntegrationManager
        manager = DataIntegrationManager()
        integrated_data = manager.integrate_data()
        manager.export_to_strategy_kg()
        print("✓ 数据整合成功")
        print(f"整合后知识点数量: {integrated_data.get('metadata', {}).get('total_concepts', 0)}")
        print(f"整合后关系数量: {integrated_data.get('metadata', {}).get('total_relations', 0)}")
        print(f"整合后课程数量: {integrated_data.get('metadata', {}).get('total_courses', 0)}")
        print(f"整合后资源数量: {integrated_data.get('metadata', {}).get('total_resources', 0)}")
    except Exception as e:
        print(f"数据整合失败: {e}")
    
    print("\n" + "=" * 60)
    print("所有数据源采集完成！")

if __name__ == "__main__":
    main()
