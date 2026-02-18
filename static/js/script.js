// Animate cards on scroll
document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll(".work-card");

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("animate-card");
        }
      });
    },
    { threshold: 0.5 },
  );

  cards.forEach((card) => observer.observe(card));
});

// Scroll to top on page load
window.addEventListener("load", () => {
  window.scrollTo({ top: 0, behavior: "smooth" });
});

// Scroll to jobs section if filter/search applied
window.addEventListener("load", () => {
  if (window.location.search.length > 0) {
    const jobsSection = document.getElementById("jobs-section");
    if (jobsSection) {
      jobsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }
});
