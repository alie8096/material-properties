import markdown
from jinja2 import Template
import re
import htmlmin
import pdfkit  # اضافه کردن کتابخانه pdfkit

# خواندن فایل Markdown
with open('slides.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

# تفکیک صفحات بر اساس '^^^'
slides = md_content.split('^^^')

# تنظیمات افزونه‌ها برای پردازش دقیق‌تر Markdown
md_extensions = ['fenced_code', 'tables', 'attr_list', 'nl2br', 'extra']

# تبدیل Markdown به HTML و شناسایی انواع محتوا
html_pages = []
# متغیری برای بررسی اینکه آیا intro-container اضافه شده است یا خیر
intro_section_added = False

for i, slide in enumerate(slides):
    html_slide = markdown.markdown(slide, extensions=md_extensions)

    # اصلاح الگوی regex برای محیط‌های LaTeX
    html_slide = re.sub(
        r'\$\$\s*([\s\S]*?)\s*\$\$',
        r'<div class="math-formula">$$\1$$</div>',
        html_slide
    )

    # تبدیل بلوک‌های \[...\] به div با کلاس math-formula
    html_slide = re.sub(
        r'\\\[(.*?)\\\]',
        r'<div class="math-formula">$$\1$$</div>',
        html_slide
    )

    # فرمول‌های اینلاین LaTeX
    html_slide = re.sub(
        r'(?<!\$)\$(?!\$)(.*?)\$(?!\$)',
        r'<span class="math-inline">$\1$</span>',
        html_slide
    )

    # تبدیل فرمول‌های اینلاین \(...\) به span با کلاس math-inline
    html_slide = re.sub(
        r'\\\((.*?)\\\)',
        r'<span class="math-inline">$\1$</span>',
        html_slide
    )

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

    # شناسایی و اضافه کردن intro-container فقط برای اولین اسلاید
    if i == 0 and not intro_section_added:
        # پیدا کردن h1 و اولین h2
        h1_match = re.search(r'(<h1.*?>.*?</h1>)', html_slide)
        h2_match = re.search(r'(<h2.*?>.*?</h2>)', html_slide)

        if h1_match and h2_match:
            # ساختار intro-container شامل h1 و h2
            intro_content = f'<div class="intro-container">{
                h1_match.group(1)}{h2_match.group(1)}</div>'

            # حذف h1 و اولین h2 از محتوای اسلاید اصلی
            html_slide = re.sub(r'<h1.*?>.*?</h1>', '', html_slide)
            html_slide = re.sub(r'<h2.*?>.*?</h2>', '', html_slide)

            # افزودن intro-container به اولین section (slide-1)
            html_slide = intro_content + html_slide

            intro_section_added = True  # مشخص می‌کنیم که intro اضافه شده است

    # اضافه کردن اسلاید به صفحات
    html_pages.append(
        f'<section id="slide-{i+1}" class="slide">{html_slide}</section>')


# قالب HTML برای اسلایدر
html_template = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Material Properties</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="https://github.com/alie8096/alie8096/blob/main/Images/logo.svg" type="image/svg">
  <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font/dist/font-face.css" rel="stylesheet">
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
  
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="container">
    <div class="reveal">
      <div class="slides">
        {{ content }}
      </div>
    </div>
    <div class="navigation">
      <input type="number" id="slideNumberInput" min="1" max="{{ totalSlides }}">
      <span id="totalSlides">از {{ totalSlides }}</span>
    </div>
  </div>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.3.1/reveal.min.js"></script>
  <script>
      Reveal.initialize();

      const totalSlides = {{ totalSlides }};
      const input = document.getElementById('slideNumberInput');

      // تنظیم ورودی شماره اسلاید فعلی
      Reveal.on('slidechanged', function(event) {
        input.value = Reveal.getIndices().h + 1;
      });

      // جستجو و حرکت به اسلاید بر اساس شماره
      input.addEventListener('change', function() {
        const persianNumbers = '۰۱۲۳۴۵۶۷۸۹';
        let inputValue = input.value.trim(); // حذف فضای خالی

        // تبدیل اعداد فارسی به انگلیسی
        let slideNumber = inputValue.split('').map(c => {
          return persianNumbers.includes(c) ? persianNumbers.indexOf(c) : c;
        }).join('');

        // بررسی معتبر بودن عدد
        slideNumber = parseInt(slideNumber, 10); // پایه ۱۰ برای اطمینان از تبدیل صحیح

        if (!isNaN(slideNumber) && slideNumber >= 1 && slideNumber <= totalSlides) {
          Reveal.slide(slideNumber - 1);
        } else {
          alert('شماره اسلاید معتبر نیست');
          input.value = Reveal.getIndices().h + 1;
        }
      });

      // مقداردهی اولیه ورودی شماره اسلاید
      input.value = Reveal.getIndices().h + 1;

      Reveal.initialize({
        width: '100%',
        height: '100%',
        margin: 0.1, // کاهش فاصله‌های داخلی
        minScale: 1,
        maxScale: 2
      });
      
      (function() {
        const message = document.createElement('div');
        message.id = 'rotate-message';
        message.style.display = 'none';
        message.style.width = '100%';
        message.style.height = '100%';
        message.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        message.style.color = 'white';
        message.style.fontSize = '18px';
        message.style.textAlign = 'center';
        message.style.zIndex = '1000';
        message.textContent = 'لطفاً دستگاه خود را به حالت افقی بچرخانید';
        document.body.appendChild(message);
        function checkOrientation() {
            if (window.innerHeight > window.innerWidth) {
                message.style.display = 'flex';
                message.style.justifyContent = "center"
                message.style.alignItems = "Center"
                document.body.style.overflow = 'hidden'; // مخفی کردن overflow
                document.querySelector(".container").style.display = "none";
            } else {
                message.style.display = 'none';
                document.body.style.overflow = 'auto'; // اجازه overflow در حالت لند اسکیپ
                document.querySelector(".container").style.display = "block"; 
            }
        }
    
        window.addEventListener('resize', checkOrientation);
        window.addEventListener('load', checkOrientation);
    })();
  </script>
</body>
</html>
"""

# استفاده از Jinja2 برای ترکیب HTML و محتوای تبدیل شده
template = Template(html_template)
output_html = template.render(content="\n".join(
    html_pages), totalSlides=len(slides))

# Minify html to faster run
minified_html = htmlmin.minify(output_html, remove_empty_space=True)

# ذخیره HTML خروجی
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(minified_html)

# تبدیل HTML به PDF با pdfkit
# options = {
#     'enable-local-file-access': '',  # دسترسی به فایل‌های محلی
#     'no-stop-slow-scripts': '',
#     'javascript-delay': '5000',  # تأخیر برای اجرای جاوااسکریپت
#     'debug-javascript': '',  # برای مشاهده مشکلات جاوااسکریپت
#     'orientation': 'Landscape',  # تنظیم صفحات به صورت افقی
#     'page-size': 'A5',  # اندازه صفحه
#     'margin-top': '5mm',  # حاشیه‌ها را به حداقل برسانید
#     'margin-right': '5mm',
#     'margin-bottom': '5mm',
#     'margin-left': '5mm',
#     'zoom': '2.0',  # افزایش زوم برای بزرگ‌تر کردن محتوای PDF
#     'load-media-error-handling': 'ignore',  # نادیده گرفتن خطاهای بارگذاری مدیا
#     'user-style-sheet': 'style.css'  # مشخص کردن فایل CSS
# }

# pdfkit.from_file('index.html', 'slides.pdf', options=options)


print("Conversion completed. Check the 'index.html' and 'slides.pdf' files.")
