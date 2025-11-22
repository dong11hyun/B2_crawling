# crawler/models.py
from django.db import models

class Seller(models.Model):
    # 사업자 번호는 겹치면 안 되니까 unique=True
    business_number = models.CharField(max_length=20, unique=True, verbose_name="사업자등록번호")
    
    company_name = models.CharField(max_length=100, verbose_name="상호명")
    ceo_name = models.CharField(max_length=50, verbose_name="대표자명", null=True, blank=True)
    contact_number = models.CharField(max_length=50, verbose_name="연락처", null=True, blank=True)
    email = models.EmailField(verbose_name="이메일", null=True, blank=True)
    
    # 언제 수집했는지 자동 기록
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="최초수집일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="최근갱신일")

    def __str__(self):
        return f"{self.company_name} ({self.business_number})"