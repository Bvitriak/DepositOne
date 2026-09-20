const FALLBACK_ABOUT = {
  name: "DepositOne",
  summary: "Internal platform for the operational tracking of deposit agreements and the viewing of analytics.",
  description: "The project description is temporarily unavailable because the supporting service does not answer.",
  author: "Bogdan Vitriak",
  group: "OKBI-204B",
  organization: "Moscow Technology Institute",
  version: "1.0",
  license: "MIT",
  stack: [],
  features: [],
};

function metaRow(label, value) {
  return `<div class="about-meta-row">
    <span class="about-meta-label">${label}</span>
    <span class="about-meta-value">${escapeHtml(value)}</span>
  </div>`;
}

function stackRow(item) {
  return `<div class="about-stack-row">
    <span class="about-stack-layer">${escapeHtml(item.layer)}</span>
    <span class="about-stack-tools">${escapeHtml(item.tools)}</span>
  </div>`;
}

function featureRow(feature) {
  return `<li class="about-feature">${escapeHtml(feature)}</li>`;
}

function aboutPage(about) {
  const stack = about.stack.length === 0
    ? `<p class="about-empty">No Information</p>`
    : about.stack.map(stackRow).join("");
  const features = about.features.length === 0
    ? `<p class="about-empty">No Information</p>`
    : `<ul class="about-features">${about.features.map(featureRow).join("")}</ul>`;
  return `<div class="about-layout">
    <section class="about-story panel">
      <h2 class="about-title">What the platform does</h2>
      <p class="about-description">${escapeHtml(about.description)}</p>
      <h2 class="about-title">Features</h2>
      ${features}
    </section>
    <aside class="about-side">
      <section class="about-card panel">
        <h2 class="about-title">Technology</h2>
        <div class="about-stack">${stack}</div>
      </section>
      <section class="about-card panel">
        <h2 class="about-title">Project</h2>
        <div class="about-meta">
          ${metaRow("Author", about.author)}
          ${metaRow("Group", about.group)}
          ${metaRow("Organization", about.organization)}
          ${metaRow("Version", about.version)}
          ${metaRow("License", about.license)}
        </div>
      </section>
    </aside>
  </div>`;
}

async function loadAbout() {
  let about = FALLBACK_ABOUT;
  try {
    const response = await fetch("/api/about");
    if (response.ok) {
      about = await response.json();
    }
  } catch {
    about = FALLBACK_ABOUT;
  }
  document.getElementById("aboutName").textContent = about.name;
  document.getElementById("aboutSummary").textContent = about.summary;
  document.title = "DepositOne About";
  document.getElementById("about").innerHTML = aboutPage(about);
}

loadAbout();
