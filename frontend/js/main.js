const burger = document.getElementById("burger");
const menu = document.getElementById("menu");
const menuClose = document.getElementById("menuClose");

burger.addEventListener("click", () => menu.classList.add("open"));
menuClose.addEventListener("click", () => menu.classList.remove("open"));
menu.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => menu.classList.remove("open"));
});
