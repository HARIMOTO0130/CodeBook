# 数据采集系统配置

# 数据源配置
DATA_SOURCES = {
    "mooccube": {
        "name": "MOOCCube",
        "description": "计算机科学MOOC课程数据",
        "url": "https://mooccube.github.io/",
        "enabled": True
    },
    "wikidata": {
        "name": "Wikidata",
        "description": "通用知识库",
        "api_url": "https://www.wikidata.org/w/api.php",
        "sparql_url": "https://query.wikidata.org/sparql",
        "enabled": True
    },
    "dbpedia": {
        "name": "DBpedia",
        "description": "从Wikipedia提取的结构化数据",
        "sparql_url": "https://dbpedia.org/sparql",
        "enabled": True
    },
    "education_platforms": {
        "name": "在线教育平台",
        "description": "Coursera、edX、B站、YouTube、LeetCode",
        "enabled": True,
        "platforms": {
            "coursera": {
                "api_url": "https://api.coursera.org/api/courses.v1"
            },
            "edx": {
                "api_url": "https://www.edx.org/api/v2/courses"
            },
            "bilibili": {
                "api_url": "https://api.bilibili.com"
            },
            "youtube": {
                "api_url": "https://www.googleapis.com/youtube/v3"
            },
            "leetcode": {
                "api_url": "https://leetcode.com/api"
            }
        }
    },
    "textbooks": {
        "name": "教材与文档",
        "description": "经典教材和官方文档",
        "enabled": True,
        "resources": [
            {"name": "CSAPP", "url": "https://csapp.cs.cmu.edu/"},
            {"name": "算法导论", "url": "https://mitpress.mit.edu/books/introduction-algorithms"},
            {"name": "Python官方文档", "url": "https://docs.python.org/3/"},
            {"name": "MDN文档", "url": "https://developer.mozilla.org/"}
        ]
    }
}

# 数据存储配置
STORAGE_CONFIG = {
    "base_path": "data_collection/storage",
    "formats": {
        "raw": "json",
        "processed": "json",
        "final": "json"
    },
    "max_file_size": 104857600  # 100MB
}

# 数据处理配置
PROCESSING_CONFIG = {
    "batch_size": 1000,
    "max_retries": 3,
    "timeout": 30,
    "rate_limit": {
        "wikidata": 10,  # 请求/秒
        "dbpedia": 5,    # 请求/秒
        "education_platforms": 2  # 请求/秒
    }
}

# 数据质量控制配置
QUALITY_CONFIG = {
    "validation": {
        "required_fields": ["concept_id", "concept_name", "course_id", "prerequisites", "successors"],
        "min_confidence": 0.7
    },
    "cleaning": {
        "remove_duplicates": True,
        "normalize_names": True,
        "fix_encoding": True
    }
}

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "data_collection/logs/data_collection.log"
}