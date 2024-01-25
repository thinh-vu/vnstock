Chèn đoạn code sau vào cuối trang `docs\docs\material\overrides\main.html` -sau dòng 10 để hiển thị banner thông báo.


{% block announce %}
<!-- Add a panorama banner here -->
<div style="width: 100%; overflow: hidden; position: relative;">
  <a href="https://docs.vnstock.site/course/" style="display: block; width: 100%; height: 100%;">
      <img src="https://docs.vnstock.site/assets/images/banner_python_course_5_phan_tich_va_giao_dich_ck_trong_python.jpg?raw=true" alt="Thông báo quan trọng" style="width: 100%; height: 100%; object-fit: cover;">
  </a>
</div>
{% endblock %}