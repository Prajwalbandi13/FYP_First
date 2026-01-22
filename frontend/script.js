const form = document.getElementById("uploadForm");
const imageInput = document.getElementById("imageInput");
const previewDiv = document.getElementById("preview");
const resultDiv = document.getElementById("result");

const diseaseSpan = document.getElementById("disease");
const confidenceSpan = document.getElementById("confidence");
const severitySpan = document.getElementById("severity");

const geminiResultsDiv = document.getElementById("gemini-results");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const file = imageInput.files[0];
    if (!file) {
        alert("Please select an image");
        return;
    }

    /* ---------------- IMAGE PREVIEW ---------------- */
    previewDiv.innerHTML = "";
    const img = document.createElement("img");
    img.src = URL.createObjectURL(file);
    img.style.maxWidth = "300px";
    img.style.borderRadius = "10px";
    previewDiv.appendChild(img);

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("http://127.0.0.1:8000/detect", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const errText = await response.text();
            console.error("Backend error:", errText);
            alert("Backend returned an error");
            return;
        }

        const data = await response.json();
        console.log("Backend response:", data);

        /* ---------------- LEFT PANEL RESULT ---------------- */
        diseaseSpan.textContent = data["Predicted Disease"];
        confidenceSpan.textContent = `${data["Confidence"]}%`;

        const severity = data["Severity (AI-estimated)"];
        severitySpan.textContent = severity;

        resultDiv.classList.remove("hidden");

        /* ---------------- RIGHT PANEL (GEMINI) ---------------- */
        const guidanceText = data["Medical Guidance"];

        geminiResultsDiv.innerHTML = `
            <h3>📌 Medical Guidance</h3>
            <div class="guidance">
                ${formatGuidance(guidanceText)}
            </div>
        `;

    } catch (error) {
        console.error("Fetch failed:", error);
        alert("Error connecting to backend");
    }
});

/* ---------------- FORMAT GEMINI TEXT ---------------- */
function formatGuidance(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\n\s*\*\s+/g, "<li>")
        .replace(/(<li>.*)/g, "<ul>$1</ul>")
        .replace(/\n/g, "<br>");
}
