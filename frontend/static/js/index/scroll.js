
document.addEventListener("DOMContentLoaded", () => {
    const scrollBtn = document.getElementById("scrollToFeatures");
    const target = document.getElementById("features");

    if (scrollBtn && target) {
    scrollBtn.addEventListener("click", (e) => {
        e.preventDefault();

        const offset = 0; // например, если есть фиксированная шапка — поставь её высоту здесь
        const top = target.getBoundingClientRect().top + window.pageYOffset - offset;

        window.scrollTo({
        top,
        behavior: "smooth"
        });
    });
    }
});
