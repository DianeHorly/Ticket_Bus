// theme-toggle.js

document.addEventListener("DOMContentLoaded", function () {
    const body = document.body;
    const toggleBtn = document.getElementById("themeToggle");

    if (!toggleBtn) return;

    // Appliquer le thème déjà choisi (s’il existe)
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark") {
        body.classList.add("bg-dark", "text-white");
    }

    // Gérer le clic sur l’icône
    toggleBtn.addEventListener("click", function () {
        body.classList.toggle("bg-dark");
        body.classList.toggle("text-white");

        // Sauvegarder le choix dans le stockage local
        const isDark = body.classList.contains("bg-dark");
        localStorage.setItem("theme", isDark ? "dark" : "light");

        // Changer l’icône
        this.innerHTML = isDark ? "☀️" : "🌙";
    });
});
