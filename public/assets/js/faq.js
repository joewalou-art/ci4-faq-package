document.addEventListener('DOMContentLoaded', function () {
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(item => {
        const button = item.querySelector('.faq-question');

        button.addEventListener('click', () => {
            const isOpen = item.classList.contains('open');

            faqItems.forEach(other => {
                other.classList.remove('open');
                const otherButton = other.querySelector('.faq-question');
                otherButton.setAttribute('aria-expanded', 'false');
            });

            if (!isOpen) {
                item.classList.add('open');
                button.setAttribute('aria-expanded', 'true');
            }
        });
    });

    const searchInput = document.getElementById('faqSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            const keyword = this.value.trim().toLowerCase();
            const items = document.querySelectorAll('.faq-item');

            items.forEach(item => {
                const question = item.querySelector('.faq-question span')?.textContent.toLowerCase() || '';
                const answer = item.querySelector('.faq-answer')?.textContent.toLowerCase() || '';
                const match = !keyword || question.includes(keyword) || answer.includes(keyword);
                item.style.display = match ? 'block' : 'none';
            });
        });
    }
});
