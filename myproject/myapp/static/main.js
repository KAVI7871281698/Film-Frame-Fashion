document.addEventListener("DOMContentLoaded", () => {

    /* ================= STICKY HEADER ================= */
    const header = document.querySelector(".header");

    if (header) {
        window.addEventListener("scroll", () => {
            header.classList.toggle("fixed", window.scrollY > 80);
        });
    }

    /* ================= MOBILE MENU TOGGLE ================= */
    window.toggleMenu = () => {
        const navbar = document.querySelector(".navbar");
        if (navbar) {
            navbar.classList.toggle("active");
        }
    };

    /* ================= DOT SLIDER (SAFE) ================= */
    let dots = document.querySelectorAll(".dot");

    if (dots.length > 0) {
        let index = 0;

        const updateDots = () => {
            dots.forEach((dot, i) => {
                dot.classList.toggle("active", i === index);
            });
        };

        updateDots();

        setInterval(() => {
            index = (index + 1) % dots.length;
            updateDots();
        }, 2000);
    }

});
