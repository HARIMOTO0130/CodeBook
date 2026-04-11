import scrapy
from scrapy.crawler import CrawlerProcess
from data_collection.storage.storage_manager import StorageManager
from data_collection.utils.data_models import KnowledgeNode, Resource

class TextbookSpider(scrapy.Spider):
    """教材和文档爬虫基类"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage = StorageManager()
    
    def parse(self, response):
        """解析响应"""
        pass

class CSAPPSpider(TextbookSpider):
    """CSAPP教材爬虫"""
    name = 'csapp'
    start_urls = ['https://csapp.cs.cmu.edu/']
    
    def parse(self, response):
        # 提取CSAPP目录结构
        chapters = []
        # 这里需要根据实际页面结构调整选择器
        for idx, chapter in enumerate(response.css('div.chapter')):
            chapter_name = chapter.css('h2::text').get() or chapter.css('h3::text').get()
            if chapter_name:
                node = KnowledgeNode(
                    concept_id=f"csapp_chapter_{idx+1}",
                    concept_name=chapter_name.strip(),
                    course_id="CSAPP",
                    prerequisites=[],
                    successors=[],
                    level=1,  # 分类层
                    category="textbook_chapter",
                    description=f"CSAPP教材第{idx+1}章",
                    source="CSAPP",
                    depth=0,
                    parent_concept=None,
                    keywords=[chapter_name.strip(), "CSAPP"],
                    difficulty=1,
                    importance=1
                )
                chapters.append(node.to_dict())
        
        # 保存数据
        self.storage.save_raw_data('textbooks', 'csapp', {'chapters': chapters})
        self.storage.save_processed_data('textbooks', 'csapp', chapters)
        
        self.logger.info(f"采集到 {len(chapters)} 个CSAPP章节")
        return chapters

class PythonDocsSpider(TextbookSpider):
    """Python官方文档爬虫"""
    name = 'python_docs'
    start_urls = ['https://docs.python.org/3/contents.html']
    
    def parse(self, response):
        # 提取Python文档目录结构
        sections = []
        
        # 提取主要章节
        for idx, section in enumerate(response.css('div#the-python-standard-library ul li a')):
            section_name = section.css('::text').get()
            section_url = section.css('::attr(href)').get()
            
            if section_name and section_url:
                node = KnowledgeNode(
                    concept_id=f"python_docs_section_{idx+1}",
                    concept_name=section_name.strip(),
                    course_id="Python官方文档",
                    prerequisites=[],
                    successors=[],
                    level=1,  # 分类层
                    category="documentation_section",
                    description=f"Python官方文档: {section_name.strip()}",
                    source="Python官方文档",
                    depth=0,
                    parent_concept=None,
                    keywords=[section_name.strip(), "Python"],
                    difficulty=1,
                    importance=1
                )
                sections.append(node.to_dict())
        
        # 保存数据
        self.storage.save_raw_data('textbooks', 'python_docs', {'sections': sections})
        self.storage.save_processed_data('textbooks', 'python_docs', sections)
        
        self.logger.info(f"采集到 {len(sections)} 个Python文档章节")
        return sections

class CSDNTutorialSpider(TextbookSpider):
    """CSDN技术博客爬虫"""
    name = 'csdn_tutorial'
    start_urls = [
        'https://blog.csdn.net/column/details/16436.html',  # Python系列教程
        'https://blog.csdn.net/column/details/16437.html',  # Java系列教程
        'https://blog.csdn.net/column/details/16438.html'   # 前端系列教程
    ]
    
    def parse(self, response):
        # 提取系列文章的层级结构
        tutorials = []
        
        # 提取文章列表
        for idx, article in enumerate(response.css('div.article-item')):
            article_title = article.css('h2 a::text').get()
            article_url = article.css('h2 a::attr(href)').get()
            
            if article_title and article_url:
                node = KnowledgeNode(
                    concept_id=f"csdn_tutorial_{idx+1}",
                    concept_name=article_title.strip(),
                    course_id=None,
                    prerequisites=[],
                    successors=[],
                    level=2,  # 实体层
                    category="tutorial",
                    description=f"CSDN教程: {article_title.strip()}",
                    source="CSDN",
                    depth=0,
                    parent_concept=None,
                    keywords=[article_title.strip(), "tutorial"],
                    difficulty=1,
                    importance=1
                )
                tutorials.append(node.to_dict())
        
        # 保存数据
        self.storage.save_raw_data('textbooks', 'csdn_tutorials', {'tutorials': tutorials})
        self.storage.save_processed_data('textbooks', 'csdn_tutorials', tutorials)
        
        self.logger.info(f"采集到 {len(tutorials)} 个CSDN教程")
        return tutorials

class JuejinTutorialSpider(TextbookSpider):
    """掘金技术博客爬虫"""
    name = 'juejin_tutorial'
    start_urls = [
        'https://juejin.cn/column/6854594919264299015',  # 前端系列
        'https://juejin.cn/column/6854594919264299016',  # 后端系列
        'https://juejin.cn/column/6854594919264299017'   # 算法系列
    ]
    
    def parse(self, response):
        # 提取掘金系列文章
        tutorials = []
        
        # 提取文章列表
        for idx, article in enumerate(response.css('div.article-item')):
            article_title = article.css('h2 a::text').get()
            article_url = article.css('h2 a::attr(href)').get()
            
            if article_title and article_url:
                node = KnowledgeNode(
                    concept_id=f"juejin_tutorial_{idx+1}",
                    concept_name=article_title.strip(),
                    course_id=None,
                    prerequisites=[],
                    successors=[],
                    level=2,  # 实体层
                    category="tutorial",
                    description=f"掘金教程: {article_title.strip()}",
                    source="掘金",
                    depth=0,
                    parent_concept=None,
                    keywords=[article_title.strip(), "tutorial"],
                    difficulty=1,
                    importance=1
                )
                tutorials.append(node.to_dict())
        
        # 保存数据
        self.storage.save_raw_data('textbooks', 'juejin_tutorials', {'tutorials': tutorials})
        self.storage.save_processed_data('textbooks', 'juejin_tutorials', tutorials)
        
        self.logger.info(f"采集到 {len(tutorials)} 个掘金教程")
        return tutorials

def run_spiders():
    """运行所有爬虫"""
    process = CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 1
    })
    
    process.crawl(CSAPPSpider)
    process.crawl(PythonDocsSpider)
    process.crawl(CSDNTutorialSpider)
    process.crawl(JuejinTutorialSpider)
    
    process.start()

if __name__ == "__main__":
    run_spiders()