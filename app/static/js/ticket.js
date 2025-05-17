// static/js/ticket.js
// Ce script gère l'affichage dynamique du champ "validité" selon le type de ticket

document.addEventListener("DOMContentLoaded", () => {
    const typeSelect = document.getElementById("type-ticket");
    const validityContainer = document.getElementById("validity_container");
    const validityInput = document.getElementById("validity_days");

    // verification de l'existence des diverds éléments avant de les manipuler
    if (!typeSelect || !validityContainer || !validityInput) {
        console.warn("Éléments du formulaire non trouvés dans la page.");
        return;
    }

    /**
     * Met à jour l'affichage du champ de validité
     */
    const toggleValidityField = () => {
        const selectedType = typeSelect.value.trim().toLowerCase();
        const showField = selectedType === "personnalisé";

        validityContainer.style.display = showField ? "block" : "none";

        if (!showField) {
            validityInput.value = "";
            validityInput.removeAttribute("required");
            validityInput.setCustomValidity(""); // Supprime tout message d'erreur
        } else {
            validityInput.setAttribute("required", "required");
        }

        validateInput(); // S'assure que la validation est mise à jour
    };

    /**
     * Valide la valeur entrée pour la validité personnalisée
     */
    const validateInput = () => {
        // Si le champ est masqué, on ne valide rien
        if (validityContainer.style.display === "none") {
            validityInput.setCustomValidity("");
            return;
        }

        const val = parseInt(validityInput.value, 10);
        if (isNaN(val) || val < 1 || val > 365) {
            validityInput.setCustomValidity("Veuillez entrer une valeur entre 1 et 365 jours.");
        } else {
            validityInput.setCustomValidity("");
        }
    };

    // Événements
    typeSelect.addEventListener("change", toggleValidityField);
    validityInput.addEventListener("input", validateInput);

    // Initialisation
    toggleValidityField();
});
