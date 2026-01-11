"""Jupyter Notebook相关模型定义"""
from django.db import models
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class JupyterNotebook(models.Model):
    """Jupyter Notebook模型 - 符合标准Jupyter格式"""
    id = models.AutoField(primary_key=True)
    chapter = models.OneToOneField(
        'Chapter', 
        on_delete=models.CASCADE, 
        related_name='jupyter_notebook', 
        verbose_name='关联章节'
    )
    
    # Jupyter Notebook标准结构字段
    nbformat = models.IntegerField(default=4, verbose_name='Jupyter格式版本')
    nbformat_minor = models.IntegerField(default=5, verbose_name='Jupyter格式次版本')
    
    # metadata存储为JSON字段
    metadata = models.JSONField(
        default=dict, 
        verbose_name='Jupyter元数据',
        help_text='存储kernelspec、language_info等Jupyter标准元数据'
    )
    
    # 单独的cells表关联
    # cells将通过JupyterCell模型的外键关联
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'Jupyter笔记本'
        verbose_name_plural = 'Jupyter笔记本'
    
    def __str__(self):
        return f"Jupyter Notebook: {self.chapter.title}"
    
    def to_standard_format(self):
        """转换为标准Jupyter Notebook JSON格式"""
        cells_data = []
        for cell in self.cells.order_by('order'):
            cells_data.append(cell.to_dict())
        
        return {
            "cells": cells_data,
            "metadata": self.metadata,
            "nbformat": self.nbformat,
            "nbformat_minor": self.nbformat_minor
        }
    
    def from_standard_format(self, notebook_data):
        """从标准Jupyter Notebook JSON格式加载数据"""
        try:
            # 更新基本信息
            self.nbformat = notebook_data.get('nbformat', 4)
            self.nbformat_minor = notebook_data.get('nbformat_minor', 5)
            self.metadata = notebook_data.get('metadata', {})
            
            # 保存当前实例以获取ID
            self.save()
            
            # 更新cells
            self.cells.all().delete()  # 删除现有cells
            
            for order, cell_data in enumerate(notebook_data.get('cells', [])):
                cell = JupyterCell(
                    notebook=self,
                    cell_type=cell_data.get('cell_type', 'code'),
                    source=cell_data.get('source', ''),
                    execution_count=cell_data.get('execution_count'),
                    metadata=cell_data.get('metadata', {}),
                    order=order
                )
                
                # 处理outputs（仅code类型有outputs）
                if cell.cell_type == 'code':
                    cell.save()  # 先保存cell以获取ID
                    for output_data in cell_data.get('outputs', []):
                        JupyterOutput(
                            cell=cell,
                            output_type=output_data.get('output_type'),
                            data=output_data.get('data', {}),
                            execution_count=output_data.get('execution_count'),
                            ename=output_data.get('ename'),
                            evalue=output_data.get('evalue'),
                            traceback=output_data.get('traceback')
                        ).save()
                else:
                    cell.save()
            
            return True
        except Exception as e:
            logger.error(f"Failed to load Jupyter Notebook data: {str(e)}")
            return False


class JupyterCell(models.Model):
    """Jupyter Notebook单元格模型"""
    id = models.AutoField(primary_key=True)
    notebook = models.ForeignKey(
        JupyterNotebook, 
        on_delete=models.CASCADE, 
        related_name='cells', 
        verbose_name='所属Notebook'
    )
    
    # 单元格类型：code、markdown、raw
    cell_type = models.CharField(
        max_length=20, 
        choices=[('code', '代码'), ('markdown', 'Markdown'), ('raw', '原始')],
        default='code',
        verbose_name='单元格类型'
    )
    
    # 源代码内容
    source = models.TextField(blank=True, default='', verbose_name='源代码')
    
    # 仅代码单元格使用
    execution_count = models.IntegerField(null=True, blank=True, verbose_name='执行计数')
    
    # 单元格元数据
    metadata = models.JSONField(default=dict, verbose_name='单元格元数据')
    
    # 排序字段
    order = models.IntegerField(default=0, verbose_name='排序')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'Jupyter单元格'
        verbose_name_plural = 'Jupyter单元格'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.cell_type} Cell {self.order} in {self.notebook.chapter.title}"
    
    def to_dict(self):
        """转换为标准Jupyter单元格字典格式"""
        result = {
            "cell_type": self.cell_type,
            "source": self.source,
            "metadata": self.metadata
        }
        
        if self.cell_type == 'code':
            result["execution_count"] = self.execution_count
            result["outputs"] = [output.to_dict() for output in self.outputs.all()]
        
        return result


class JupyterOutput(models.Model):
    """Jupyter代码单元格输出模型"""
    id = models.AutoField(primary_key=True)
    cell = models.ForeignKey(
        JupyterCell, 
        on_delete=models.CASCADE, 
        related_name='outputs', 
        verbose_name='所属单元格'
    )
    
    # 输出类型
    output_type = models.CharField(
        max_length=20, 
        choices=[
            ('stream', '流'),
            ('display_data', '显示数据'),
            ('execute_result', '执行结果'),
            ('error', '错误'),
            ('clear_output', '清除输出')
        ],
        verbose_name='输出类型'
    )
    
    # 输出内容数据
    data = models.JSONField(default=dict, verbose_name='输出数据')
    
    # 错误相关字段
    ename = models.CharField(max_length=100, null=True, blank=True, verbose_name='错误名称')
    evalue = models.TextField(null=True, blank=True, verbose_name='错误值')
    traceback = models.JSONField(null=True, blank=True, verbose_name='错误栈')
    
    # 执行计数
    execution_count = models.IntegerField(null=True, blank=True, verbose_name='执行计数')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = 'Jupyter输出'
        verbose_name_plural = 'Jupyter输出'
    
    def __str__(self):
        return f"{self.output_type} Output for Cell {self.cell.order}"
    
    def to_dict(self):
        """转换为标准Jupyter输出字典格式"""
        result = {
            "output_type": self.output_type
        }
        
        if self.output_type in ['display_data', 'execute_result']:
            result["data"] = self.data
            result["metadata"] = {}
            if self.execution_count is not None:
                result["execution_count"] = self.execution_count
        elif self.output_type == 'stream':
            # 简化处理，实际可能需要更复杂的流数据处理
            if self.data:
                result.update(self.data)
        elif self.output_type == 'error':
            result["ename"] = self.ename or ''
            result["evalue"] = self.evalue or ''
            result["traceback"] = self.traceback or []
        
        return result