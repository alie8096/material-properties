import markdown
from jinja2 import Template
import re
import htmlmin
from weasyprint import HTML, CSS
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
        r'<li>(?!<p)(.*?)</li>', r'<li><p class="text">\1</p></li>', html_slide)  # متون
    html_slide = re.sub(r'<ul>', r'<ul class="list">', html_slide)  # لیست‌ها
    html_slide = re.sub(r'<ol>', r'<ol class="list">',
                        html_slide)  # لیست‌های شماره‌دار
    html_slide = re.sub(
        r'<a href=', r'<a class="link" href=', html_slide)  # لینک‌ها

    # اضافه کردن کلاس img-table به تصاویری که داخل td هستند
    html_slide = re.sub(r'(<td>\s*<img )',
                        r'\1class="image img-table" ', html_slide)

    # اضافه کردن کلاس image به سایر تصاویر
    html_slide = re.sub(r'(<img(?!.*class="))',
                        r'<img class="image" ', html_slide)

    # جداول
    html_slide = re.sub(
        r'<table>', r'<table class="table">', html_slide)  # جداول

    # شناسایی و اضافه کردن intro-container فقط برای اولین اسلاید
    if i == 0 and not intro_section_added:
        h1_match = re.search(r'(<h1.*?>.*?</h1>)', html_slide)
        h2_match = re.search(r'(<h2.*?>.*?</h2>)', html_slide)

        if h1_match and h2_match:
            intro_content = f'<div class="intro-container">{
                h1_match.group(1)}{h2_match.group(1)}</div>'
            html_slide = re.sub(r'<h1.*?>.*?</h1>', '', html_slide)
            html_slide = re.sub(r'<h2.*?>.*?</h2>', '', html_slide)
            html_slide = intro_content + html_slide
            intro_section_added = True

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
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">

  
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

  <div id="toolbar">
    <button class="icon-button" onclick="setTool('pencil')">
      <img src="images/pen-solid.svg" alt="Pencil" title="مداد">
    </button>
    <button class="icon-button" onclick="setTool('highlighter')">
      <img src="images/highlighter-solid.svg" alt="Highlighter" title="هایلایت">
    </button>
    <button class="icon-button" onclick="setTool('rectangle')">
      <img src="images/square-regular.svg" alt="Rectangle" title="رسم مستطیل">
    </button>
    <button class="icon-button" onclick="setTool('circle')">
      <img src="images/circle-regular.svg" alt="Circle" title="رسم دایره">
    </button>
    <input type="color" id="color-picker" value="\#000000" title="رنگ قلم">
    <button class="icon-button" onclick="clearCanvas()">
      <img src="images/eraser-solid.svg" alt="Clear" title="پاک کردن تخته">
    </button>
  </div>

  <canvas id="whiteboard-canvas"></canvas>

  <button class="toggle-button" onclick="toggleWhiteboard()"><i class="fa-solid fa-pen-to-square"></i></button>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.3.1/reveal.min.js"></script>
  <script>
      let canvas = document.getElementById('whiteboard-canvas');
      let ctx = canvas.getContext('2d');
      let drawing = false;
      let startX, startY;
      let currentColor = '\#000000';
      let tool = 'pencil';
      let isWhiteboardVisible = false;

      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;

      window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
      });

      document.getElementById('color-picker').addEventListener('input', (e) => {
        currentColor = e.target.value;
      });

      function setTool(selectedTool) {
        tool = selectedTool;
      }

      function getMousePos(canvas, evt) {
        const rect = canvas.getBoundingClientRect();
        return {
          x: evt.clientX - rect.left,
          y: evt.clientY - rect.top
        };
      }

      function getTouchPos(canvas, evt) {
        const rect = canvas.getBoundingClientRect();
        return {
          x: evt.touches[0].clientX - rect.left,
          y: evt.touches[0].clientY - rect.top
        };
      }

      canvas.addEventListener('mousedown', startDrawing);
      canvas.addEventListener('mousemove', draw);
      canvas.addEventListener('mouseup', stopDrawing);
      canvas.addEventListener('mouseleave', stopDrawing);

      canvas.addEventListener('touchstart', (e) => {
        const pos = getTouchPos(canvas, e);
        startX = pos.x;
        startY = pos.y;
        startDrawing(e);
        e.preventDefault(); // جلوگیری از رفتار پیش‌فرض
      });

      canvas.addEventListener('touchmove', (e) => {
        draw(e);
        e.preventDefault(); // جلوگیری از رفتار پیش‌فرض
      });

      canvas.addEventListener('touchend', stopDrawing);

      function startDrawing(e) {
        drawing = true;
        const pos = (e.type === 'mousedown') ? getMousePos(canvas, e) : getTouchPos(canvas, e);
        startX = pos.x;
        startY = pos.y;

        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.strokeStyle = currentColor;

        if (tool === 'highlighter') {
          ctx.globalAlpha = 0.02; // شفافیت برای هایلایتر
          ctx.lineWidth = 20; // ضخامت بیشتر
        } else {
          ctx.globalAlpha = 1.0; // بدون شفافیت برای مداد
          ctx.lineWidth = 2; // ضخامت کمتر برای مداد
        }
      }

      function draw(e) {
        if (!drawing) return;

        const mousePos = (e.type === 'mousemove') ? getMousePos(canvas, e) : getTouchPos(canvas, e);
        
        if (tool === 'rectangle') {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.beginPath();
          ctx.strokeRect(startX, startY, mousePos.x - startX, mousePos.y - startY);
          ctx.stroke(); // رسم مستطیل
        } else if (tool === 'circle') {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.beginPath();
          let radius = Math.sqrt(Math.pow(mousePos.x - startX, 2) + Math.pow(mousePos.y - startY, 2));
          ctx.arc(startX, startY, radius, 0, Math.PI * 2);
          ctx.stroke(); // رسم دایره
        } else {
          ctx.lineTo(mousePos.x, mousePos.y);
          ctx.stroke(); // رسم با مداد یا هایلایتر
        }
      }

      function stopDrawing() {
        drawing = false;
        ctx.closePath();
      }

      function clearCanvas() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }

      function toggleWhiteboard() {
        isWhiteboardVisible = !isWhiteboardVisible;
        const toolbar = document.getElementById('toolbar');
        const canvas = document.getElementById('whiteboard-canvas');

        if (isWhiteboardVisible) {
          toolbar.style.display = 'block';
          canvas.style.display = 'block';
        } else {
          toolbar.style.display = 'none';
          canvas.style.display = 'none';
        }
      }

      Reveal.initialize();

      const totalSlides = {{ totalSlides }};
      const input = document.getElementById('slideNumberInput');

      Reveal.on('slidechanged', function(event) {
        input.value = Reveal.getIndices().h + 1;
      });

      input.addEventListener('change', function() {
        const persianNumbers = '۰۱۲۳۴۵۶۷۸۹';
        let inputValue = input.value.trim();

        let slideNumber = inputValue.split('').map(c => {
          return persianNumbers.includes(c) ? persianNumbers.indexOf(c) : c;
        }).join('');

        slideNumber = parseInt(slideNumber, 10);

        if (!isNaN(slideNumber) && slideNumber >= 1 && slideNumber <= totalSlides) {
          Reveal.slide(slideNumber - 1);
        } else {
          alert('شماره اسلاید معتبر نیست');
          input.value = Reveal.getIndices().h + 1;
        }
      });

      input.value = Reveal.getIndices().h + 1;

      Reveal.initialize({
        width: '100%',
        height: '100%',
        margin: 0.1,
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
            message.style.justifyContent = "center";
            message.style.alignItems = "center";
            document.body.style.overflow = 'hidden';
            document.querySelector(".container").style.display = "none";
          } else {
            message.style.display = 'none';
            document.body.style.overflow = 'auto';
            document.querySelector(".container").style.display = "block";
          }
        }

        window.addEventListener('resize', checkOrientation);
        window.addEventListener('load', checkOrientation);
      })();
      
      // تعیین ابعاد صفحه
      const viewportHeight = window.innerHeight;
      const viewportWidth = window.innerWidth;

      // پیدا کردن تمام عناصر با مقادیر پیکسلی
      document.querySelectorAll('*').forEach(element => {
          const style = window.getComputedStyle(element);

          // جابجایی مقادیر top
          if (style.top.includes('px')) {
              const pxValue = parseFloat(style.top);
              const vhValue = (pxValue / viewportHeight) * 100;
              element.style.top = `${vhValue}vh`;
          }

          // جابجایی مقادیر left
          if (style.left.includes('px')) {
              const pxValue = parseFloat(style.left);
              const vwValue = (pxValue / viewportWidth) * 100;
              element.style.left = `${vwValue}vw`;
          }

          // تغییر دیگر مقادیر مشابه
      });

  </script>
</body>
</html>
"""


# استفاده از Jinja2 برای ترکیب HTML و محتوای تبدیل شده
template = Template(html_template)
output_html = template.render(content="\n".join(
    html_pages), totalSlides=len(slides))

# Minify html to faster
minified_html = htmlmin.minify(output_html, remove_empty_space=True)

# ذخیره HTML خروجی
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(minified_html)


# # مسیر فایل HTML که از مارک‌داون تبدیل شده
# html_path = "index.html"  # نام فایل HTML شما
# pdf_path = "output.pdf"

# # بارگذاری HTML و تبدیل به PDF
# HTML(html_path).write_pdf(
#     pdf_path,
#     stylesheets=[
#         CSS(string="""
#             @page {
#                 size: A4 landscape; /* تنظیم صفحه به صورت افقی */
#                 margin: 10mm;
#             }
#             section {
#                 page-break-after: always;
#             }
#             #toolbar {
#                 display: none; /* مخفی کردن تولبار در PDF */
#             }
#         """)
#     ]
# )


print("Conversion completed. Check the 'index.html' and 'slides.pdf' files.")
