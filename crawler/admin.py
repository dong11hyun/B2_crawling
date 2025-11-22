# crawler/admin.py
from django.contrib import admin
from .models import Seller

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    # 목록에서 보여줄 컬럼들
    list_display = ['company_name', 'business_number', 'contact_number', 'updated_at']
    # 검색 기능 추가
    search_fields = ['company_name', 'business_number']