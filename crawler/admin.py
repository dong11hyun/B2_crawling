from django.contrib import admin
from .models import Seller

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    # 1. list_display에 있는 필드명이 models.py와 정확히 일치해야 합니다.
    # (오류 원인: company_name -> seller_name 등으로 수정)
    list_display = ('rank', 'product_name', 'seller_name', 'biz_no', 'contact', 'crawled_at')
    
    # 2. 검색 필드도 모델에 있는 이름이어야 합니다.
    search_fields = ('product_name', 'seller_name', 'biz_no')
    
    # 3. 필터 필드도 마찬가지입니다.
    list_filter = ('crawled_at',)