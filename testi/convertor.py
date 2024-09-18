import markdown
from jinja2 import Template
import re

# خواندن فایل Markdown
with open('slides.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

# تفکیک صفحات بر اساس '^^^'
slides = md_content.split('^^^')

# تبدیل Markdown به HTML و شناسایی انواع محتوا
html_pages = []
for i, slide in enumerate(slides):
    html_slide = markdown.markdown(
        slide, extensions=['fenced_code', 'tables', 'attr_list', 'nl2br'])

    # افزودن کلاس‌های مناسب به انواع محتوا
    html_slide = re.sub(
        r'<p>(.*?)</p>', r'<p class="text">\1</p>', html_slide)  # متون
    html_slide = re.sub(r'<ul>', r'<ul class="list">', html_slide)  # لیست‌ها
    html_slide = re.sub(r'<ol>', r'<ol class="list">',
                        html_slide)  # لیست‌های شماره‌دار
    html_slide = re.sub(
        r'<a href=', r'<a class="link" href=', html_slide)  # لینک‌ها
    html_slide = re.sub(r'<img ', r'<img class="image" ', html_slide)  # تصاویر
    html_slide = re.sub(
        r'<table>', r'<table class="table">', html_slide)  # جداول
    html_slide = re.sub(
        # فرمول‌ها
        r'\$\$(.*?)\$\$', r'<div class="math-container">$$\1$$</div>', html_slide)

    # هر صفحه در یک section جداگانه
    html_pages.append(
        f'<section id="slide-{i+1}" class="slide">{html_slide}</section>')

# قالب HTML برای اسلایدر
html_template = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Presentation</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.3.1/reveal.min.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.3.1/theme/white.min.css">
  
  <!-- پشتیبانی از KaTeX -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.15.2/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.15.2/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.15.2/dist/contrib/auto-render.min.js"
          onload="renderMathInElement(document.body, {
              delimiters: [
                  {left: '$$', right: '$$', display: true},
                  {left: '$', right: '$', display: false},
                  {left: '\\(', right: '\\)', display: false},
                  {left: '\\[', right: '\\]', display: true}
              ],
              ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre'],
          });"></script>
  
  <style>
      /* استایل‌های سفارشی */
      body {
          font-family: 'Vazir', sans-serif;
          direction: rtl;
          text-align: right;
          line-height: 1.8;
      }
      .reveal {
          direction: ltr;  /* قرار دادن کل اسلایدر به صورت چپ به راست */
      }
      .reveal .navigate-left,
      .reveal .navigate-right {
          display: none;  /* مخفی کردن فلش‌های پیش‌فرض Reveal.js */
      }
      .slide {
          padding: 20px;
          text-align: right; /* متن‌ها به صورت راست‌چین */
      }
      .text {
          font-size: 24px;
      }
      .list {
          margin: 20px auto;
          text-align: right; /* لیست‌ها به صورت راست‌چین */
      }
      .link {
          color: blue;
          text-decoration: underline;
      }
      .image {
          max-width: 100%;
          height: auto;
      }
      .table {
          margin: 20px auto;
          width: 80%;
      }
      .math-container {
          direction: ltr;  /* فرمول‌ها به صورت چپ به راست */
          text-align: left;
          margin: 20px 0;
      }
      p {
          margin: 20px 0;
      }
      .navigation {
          position: fixed;
          bottom: 20px;
          left: 50%;
          transform: translateX(-50%);
          display: flex;
          align-items: center;
          z-index: 1000; /* اضافه کردن z-index برای قرار گرفتن دکمه‌ها بالای محتوا */
      }
      .navigation button {
          margin: 0 5px;
          padding: 8px 16px;
          background-color: #007bff;
          color: #fff;
          border: none;
          cursor: pointer;
          font-size: 16px;
      }
      .navigation input {
          width: 50px;
          text-align: center;
          font-size: 16px;
          margin: 0 5px;
          padding: 5px;
      }
      .navigation input[type="number"] {
          -moz-appearance: textfield;
      }
      .navigation input::-webkit-outer-spin-button,
      .navigation input::-webkit-inner-spin-button {
          -webkit-appearance: none;
          margin: 0;
      }
      .navigation span {
          font-size: 16px;
          color: #333;
      }
  </style>
</head>
<body>
  <div class="reveal">
    <div class="slides">
      {{ content }}
    </div>
  </div>
  <div class="navigation">
    <input type="number" id="slideNumberInput" min="1" max="{{ totalSlides }}">
    <span id="totalSlides">از {{ totalSlides }}</span>
  </div>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.3.1/reveal.min.js"></script>
  <script>
    Reveal.initialize();
    
    const totalSlides = {{ totalSlides }};
    const input = document.getElementById('slideNumberInput');

    // تنظیم ورودی شماره اسلاید فعلی
    Reveal.on('slidechanged', function(event) {
      input.value = event.indexh + 1;
    });

    // جستجو و حرکت به اسلاید بر اساس شماره
    input.addEventListener('change', function() {
      const persianNumbers = '۰۱۲۳۴۵۶۷۸۹';
      let slideNumber = input.value.split('').map(c => persianNumbers.includes(c) ? persianNumbers.indexOf(c) : c).join('');
      slideNumber = parseInt(slideNumber);
      
      if (slideNumber >= 1 && slideNumber <= totalSlides) {
        Reveal.slide(slideNumber - 1);
      } else {
        alert('شماره اسلاید معتبر نیست');
        input.value = Reveal.getIndices().h + 1;
      }
    });

    // مقداردهی اولیه ورودی شماره اسلاید
    input.value = Reveal.getIndices().h + 1;
  </script>
</body>
</html>
"""

# استفاده از Jinja2 برای ترکیب HTML و محتوای تبدیل شده
template = Template(html_template)
output_html = template.render(content="\n".join(
    html_pages), totalSlides=len(slides))

# ذخیره HTML خروجی
with open('sliders.html', 'w', encoding='utf-8') as f:
    f.write(output_html)

print("Conversion completed. Check the 'sliders.html' file.")
