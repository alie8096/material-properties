document.addEventListener("DOMContentLoaded", function () {
    function adjustContent() {
        const slides = document.querySelectorAll('.slide');
        
        slides.forEach(slide => {
            const slideWidth = slide.clientWidth;
            const slideHeight = slide.clientHeight;
            const elements = slide.children;

            Array.from(elements).forEach(element => {
                const aspectRatio = element.naturalWidth / element.naturalHeight;
                const availableWidth = slideWidth - 40; // پدینگ 20 پیکسل در هر طرف
                const availableHeight = slideHeight - 40; // پدینگ 20 پیکسل در هر طرف

                if (element.tagName === 'IMG') {
                    if (element.naturalWidth > 0 && element.naturalHeight > 0) {
                        if (aspectRatio > availableWidth / availableHeight) {
                            element.style.width = `${availableWidth}px`;
                            element.style.height = 'auto';
                        } else {
                            element.style.height = `${availableHeight}px`;
                            element.style.width = 'auto';
                        }
                    }
                } else {
                    element.style.maxWidth = '100%';
                    element.style.maxHeight = '100%';
                }
            });
        });
    }

    adjustContent();

    window.addEventListener('resize', adjustContent);
});
