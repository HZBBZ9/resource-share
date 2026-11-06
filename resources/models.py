from django.conf import settings
from django.db import models
from django.urls import reverse


class Resource(models.Model):
    """一个可供分享的资料条目。"""

    # 分类选项
    CATEGORY_CHOICES = [
        ('book', '书籍'),
        ('note', '笔记'),
        ('problem', '习题 / 试卷'),
        ('course', '课程资料'),
        ('other', '其他'),
    ]

    title = models.CharField('标题', max_length=200)
    description = models.TextField('描述', blank=True)
    category = models.CharField(
        '分类', max_length=20, choices=CATEGORY_CHOICES, default='other'
    )
    file = models.FileField('文件', upload_to='uploads/')
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='上传者',
        related_name='resources',
    )
    created_at = models.DateTimeField('上传时间', auto_now_add=True)
    download_count = models.PositiveIntegerField('下载次数', default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '资源'
        verbose_name_plural = '资源'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('resource-detail', args=[self.pk])

    @property
    def category_display_name(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)

    @property
    def file_extension(self):
        name = self.file.name or ''
        return name.rsplit('.', 1)[-1].lower() if '.' in name else ''

    @property
    def file_size_display(self):
        size = self.file.size
        if size < 1024:
            return f'{size} B'
        if size < 1024 * 1024:
            return f'{size / 1024:.1f} KB'
        if size < 1024 * 1024 * 1024:
            return f'{size / (1024 * 1024):.1f} MB'
        return f'{size / (1024 * 1024 * 1024):.1f} GB'
