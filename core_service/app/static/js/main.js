document.addEventListener("DOMContentLoaded", function () {
    const flashMessages = document.querySelectorAll(".flash");

    flashMessages.forEach((message) => {
        setTimeout(() => {
            message.style.transition = "opacity 0.5s ease";
            message.style.opacity = "0";
        }, 3000);

        setTimeout(() => {
            message.remove();
        }, 3600);
    });
});
