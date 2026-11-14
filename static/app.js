const nameEl = document.getElementById("name");
const seedEl = document.getElementById("seed");

document.getElementById("generate-btn").addEventListener("click", async () => {
  try {
    const response = await fetch("/generate?seed=" + encodeURIComponent(seedEl.value));
    const data = await response.json();
    if (response.ok) {
      nameEl.className = "";
      nameEl.textContent = data.name;
    } else {
      nameEl.className = "error";
      nameEl.textContent = data.error;
    }
  } catch (err) {
    nameEl.className = "error";
    nameEl.textContent = "Something went wrong. Please try again.";
  }
});