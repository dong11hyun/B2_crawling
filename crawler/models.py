from django.db import models

class Seller(models.Model):
    # 크롤링 기본 정보
    rank = models.IntegerField(verbose_name="순위")
    product_name = models.CharField(max_length=500, verbose_name="상품명")
    url = models.URLField(unique=True, verbose_name="상품URL")
    
    # 판매자 상세 정보
    seller_name = models.CharField(max_length=100, default="-", verbose_name="상호")
    biz_no = models.CharField(max_length=50, default="-", verbose_name="사업자번호")
    contact = models.CharField(max_length=50, default="-", verbose_name="연락처")
    
    # 관리용 필드
    crawled_at = models.DateTimeField(auto_now=True, verbose_name="수집일시")

    def __str__(self):
        return f"[{self.rank}위] {self.product_name}"

    class Meta:
        verbose_name = "쿠팡 판매자 데이터"
        verbose_name_plural = "쿠팡 판매자 데이터 목록"