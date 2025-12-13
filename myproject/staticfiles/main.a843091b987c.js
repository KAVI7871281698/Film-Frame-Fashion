document.addEventListener("DOMContentLoaded", () => {

    // Sticky Header
    window.addEventListener("scroll", () => {
        document.querySelector(".header").classList.toggle("fixed", window.scrollY > 80);
    });

    // Toggle Mobile Menu
    window.toggleMenu = () => {
        document.querySelector(".navbar").classList.toggle("active");
    };

    // Dot Slider Animation
    let index = 0;
    let dots = document.querySelectorAll(".dot");

    function updateDots() {
        dots.forEach((d, i) => d.classList.toggle("active", i === index));
    }

    setInterval(() => {
        index = (index + 1) % dots.length;
        updateDots();
    }, 2000);
});
