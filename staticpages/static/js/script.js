document.addEventListener('DOMContentLoaded', function () {
    const testimonials = document.querySelector('.testimonial-carousel');
    const testimonialItems = document.querySelectorAll('.testimonial');
    const totalTestimonials = testimonialItems.length;
    let currentTestimonial = 1;

    function showTestimonial(index) {
        testimonials.style.transform = `translateX(${-100 * (index - 1)}%)`;
        document.querySelector('.testimonial-counter').textContent = `${index} / ${totalTestimonials}`;
    }

    document.querySelector('.testimonial-nav-btn.previous').addEventListener('click', function () {
        if (currentTestimonial > 1) {
            currentTestimonial--;
            showTestimonial(currentTestimonial);
        }
    });

    document.querySelector('.testimonial-nav-btn.next').addEventListener('click', function () {
        if (currentTestimonial < totalTestimonials) {
            currentTestimonial++;
            showTestimonial(currentTestimonial);
        }
    });
});