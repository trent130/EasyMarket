document.querySelectorAll('.product-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
        card.querySelector('.product-reviews').style.display = 'block';
    });
    card.addEventListener('mouseleave', () => {
        card.querySelector('.product-reviews').style.display = 'none';
    });
});
