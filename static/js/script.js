// main.js - External JS for your site
document.addEventListener("DOMContentLoaded", () => {
  // Animate work cards on scroll
  const cards = document.querySelectorAll(".work-card");
  if (cards.length) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("animate-card");
            observer.unobserve(entry.target); // animate once
          }
        });
      },
      { threshold: 0.5 },
    );
    cards.forEach((card) => observer.observe(card));
  }

  // Auto-close navbar on mobile after clicking a link
  const navLinks = document.querySelectorAll(".navbar-nav .nav-link");
  const navCollapseEl = document.querySelector(".navbar-collapse");
  if (navCollapseEl && navLinks.length) {
    const bsCollapse = new bootstrap.Collapse(navCollapseEl, { toggle: false });

    navLinks.forEach((link) => {
      link.addEventListener("click", () => {
        if (navCollapseEl.classList.contains("show")) {
          bsCollapse.hide();
        }
      });
    });
  }
});

// Scroll to top on page load
window.addEventListener("load", () => {
  window.scrollTo({ top: 0, behavior: "smooth" });

  // Scroll to jobs section if filter/search applied
  if (window.location.search.length > 0) {
    const jobsSection = document.getElementById("jobs-section");
    if (jobsSection) {
      jobsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }
});
