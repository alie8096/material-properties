// Reveal.initialize({
//     width: '100%',
//     height: '100%',
//     margin: 0,
//     minScale: 1,
//     maxScale: 1,
//     transition: 'fade', // انیمیشن محو شدن برای تغییر اسلایدها
//     slideNumber: true // نمایش شماره اسلاید
// });

// const input = document.getElementById('slideNumberInput');

// // تنظیم شماره اسلاید بر اساس موقعیت فعلی
// Reveal.on('slidechanged', function(event) {
//     input.value = event.indexh + 1;
// });

// // جستجو و تغییر اسلاید بر اساس شماره ورودی
// input.addEventListener('change', function() {
//     const slideNumber = parseInt(input.value);
//     if (slideNumber >= 1 && slideNumber <= Reveal.getTotalSlides()) {
//         Reveal.slide(slideNumber - 1);
//     } else {
//         alert('شماره اسلاید معتبر نیست');
//         input.value = Reveal.getIndices().h + 1;
//     }
// });

// // مقداردهی اولیه ورودی
// input.value = Reveal.getIndices().h + 1;

document.addEventListener("DOMContentLoaded", function () {
    function adjustContent() {
        const slides = document.querySelectorAll('.slide');
        
        slides.forEach(slide => {
            const slideWidth = slide.clientWidth;
            const slideHeight = slide.clientHeight;
            const elements = slide.children;

            Array.from(elements).forEach(element => {
                // محاسبه نسبت عرض به ارتفاع برای تصاویر
                if (element.tagName === 'IMG' && element.naturalWidth > 0 && element.naturalHeight > 0) {
                    const aspectRatio = element.naturalWidth / element.naturalHeight;
                    const availableWidth = slideWidth - 40; // کاهش پدینگ 40 پیکسل
                    const availableHeight = slideHeight - 40;

                    // تطابق اندازه تصویر با فضای موجود
                    if (aspectRatio > availableWidth / availableHeight) {
                        element.style.width = `${availableWidth}px`;
                        element.style.height = 'auto';
                    } else {
                        element.style.height = `${availableHeight}px`;
                        element.style.width = 'auto';
                    }
                } else {
                    element.style.maxWidth = '100%';
                    element.style.maxHeight = '100%';
                }
            });
        });
    }

    // فراخوانی اولیه تنظیمات
    adjustContent();

    // تغییر اندازه محتوا در صورت تغییر اندازه صفحه
    window.addEventListener('resize', adjustContent);
});

// تنظیمات Reveal.js
Reveal.initialize({
    width: '100%',
    height: '100%',
    margin: 0,
    minScale: 1,
    maxScale: 1,
    transition: 'fade',
    slideNumber: true
});

const input = document.getElementById('slideNumberInput');

// تنظیم شماره اسلاید بر اساس موقعیت فعلی
Reveal.on('slidechanged', function(event) {
    input.value = event.indexh + 1;
});

// تغییر اسلاید بر اساس شماره ورودی
input.addEventListener('change', function() {
    const persianNumbers = '۰۱۲۳۴۵۶۷۸۹';
    let slideNumber = input.value.trim().split('').map(c => persianNumbers.includes(c) ? persianNumbers.indexOf(c) : c).join('');
    slideNumber = parseInt(slideNumber);

    if (!isNaN(slideNumber) && slideNumber >= 1 && slideNumber <= Reveal.getTotalSlides()) {
        Reveal.slide(slideNumber - 1);
    } else {
        alert('شماره اسلاید معتبر نیست');
        input.value = Reveal.getIndices().h + 1;
    }
});

// مقداردهی اولیه شماره ورودی اسلاید
input.value = Reveal.getIndices().h + 1;
