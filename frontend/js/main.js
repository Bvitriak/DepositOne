const burger = document.getElementById("burger");
const menu = document.getElementById("menu");
const menuClose = document.getElementById("menuClose");

burger.addEventListener("click", () => menu.classList.add("open"));
menuClose.addEventListener("click", () => menu.classList.remove("open"));
menu.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => menu.classList.remove("open"));
});

const stars = document.getElementById("stars");
for (let i = 0; i < 25; i++) {
  const star = document.createElement("span");
  star.className = "star";
  star.style.left = Math.random() * 100 + "%";
  star.style.top = Math.random() * 45 + "%";
  stars.appendChild(star);
}
