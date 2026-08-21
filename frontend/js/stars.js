const stars = document.getElementById("stars");
for (let i = 0; i < 25; i++) {
  const star = document.createElement("span");
  star.className = "star";
  star.style.left = Math.random() * 100 + "%";
  star.style.top = Math.random() * 45 + "%";
  stars.appendChild(star);
}
