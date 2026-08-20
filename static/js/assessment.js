/* =========================================================
   SKILLBRIDGE - ASSESSMENT JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    const sliders = [
        {
            input: "programming",
            output: "programming-value"
        },
        {
            input: "problem-solving",
            output: "problem-solving-value"
        },
        {
            input: "communication",
            output: "communication-value"
        },
        {
            input: "design",
            output: "design-value"
        }
    ];


    sliders.forEach((slider) => {

        const input = document.getElementById(slider.input);
        const output = document.getElementById(slider.output);

        if (!input || !output) {
            return;
        }


        function updateValue() {
            output.textContent = `${input.value}%`;
        }


        input.addEventListener("input", updateValue);

        updateValue();

    });

});