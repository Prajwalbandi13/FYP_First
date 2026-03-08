import React, { useMemo, useState } from "react";
import jsPDF from "jspdf";
import PatientForm from "./PatientForm";

function App() {
  const [patient, setPatient] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  const [preview, setPreview] = useState(null);
  const [disease, setDisease] = useState("");
  const [confidence, setConfidence] = useState("");
  const [severity, setSeverity] = useState("");
  const [guidance, setGuidance] = useState("");
  const [riskAnalysis, setRiskAnalysis] = useState(null);
  const [heatmap, setHeatmap] = useState(null);
  const [showHeatmap, setShowHeatmap] = useState(false);

  const numericConfidence = useMemo(() => {
    const val = Number(confidence);
    if (Number.isNaN(val)) return 0;
    return Math.max(0, Math.min(100, val));
  }, [confidence]);

  if (!patient) {
    return <PatientForm onSubmit={setPatient} />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();

    const file = e.target.image.files[0];
    if (!file) {
      alert("Please select an image");
      return;
    }

    setPreview(URL.createObjectURL(file));
    setHeatmap(null);
    setShowHeatmap(false);
    setRiskAnalysis(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("age", String(patient.age));
    formData.append("previous_disease", patient.previousDisease || "");

    try {
      const response = await fetch("http://127.0.0.1:8000/detect", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Backend responded with ${response.status}`);
      }

      const data = await response.json();

      setDisease(data["Predicted Disease"] || "");
      setConfidence(data["Confidence"] || "");
      setSeverity(data["Severity (AI-estimated)"] || "");
      setGuidance(data["Medical Guidance"] || "");
      setRiskAnalysis(data["Risk Analysis"] || null);

      if (data.heatmap) {
        setHeatmap(`data:image/jpeg;base64,${data.heatmap}`);
      }
    } catch (err) {
      console.error(err);
      alert("Backend error");
    }
  };

  const generatePDF = () => {
    const doc = new jsPDF();

    doc.setFontSize(18);
    doc.text("CureX AI Medical Report", 20, 20);

    doc.setFontSize(12);
    doc.text(`Patient: ${patient.name}`, 20, 35);
    doc.text(`Age: ${patient.age}`, 20, 45);
    doc.text(`Previous Disease: ${patient.previousDisease || "None"}`, 20, 55);

    doc.text(`Disease: ${disease}`, 20, 70);
    doc.text(`Confidence: ${confidence}%`, 20, 80);
    doc.text(`Severity: ${severity}`, 20, 90);

    if (riskAnalysis) {
      doc.text(`Risk Level: ${riskAnalysis["Risk Level"] || "N/A"}`, 20, 105);
      doc.text(`Age Impact: ${riskAnalysis["Age Impact"] || "N/A"}`, 20, 115, {
        maxWidth: 170,
      });
      doc.text(
        `Previous Disease Impact: ${riskAnalysis["Previous Disease Impact"] || "N/A"}`,
        20,
        130,
        { maxWidth: 170 }
      );
    }

    doc.save("CureX_Report.pdf");
  };

  function formatGuidance(text) {
    if (!text) return "";

    return text
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n\s*\*\s+/g, "<li>")
      .replace(/(<li>.*)/g, "<ul>$1</ul>")
      .replace(/\n/g, "<br>");
  }

  function getRiskWarning() {
    let warning = "";

    if (Number(patient.age) > 60) {
      warning += "Patients above 60 have higher lung disease risk. ";
    }

    if (
      patient.previousDisease &&
      (patient.previousDisease.toLowerCase().includes("diabetes") ||
        patient.previousDisease.toLowerCase().includes("asthma") ||
        patient.previousDisease.toLowerCase().includes("heart"))
    ) {
      warning += "Existing medical conditions may worsen lung disease severity.";
    }

    return warning;
  }

  function riskBadgeClass(level) {
    if (level === "High") {
      return "bg-red-100 text-red-700 border-red-200";
    }
    if (level === "Medium") {
      return "bg-amber-100 text-amber-700 border-amber-200";
    }
    return "bg-emerald-100 text-emerald-700 border-emerald-200";
  }

  return (
    <div
      className={`min-h-screen p-6 md:p-10 ${
        darkMode
          ? "bg-gradient-to-br from-slate-900 to-slate-800 text-slate-100"
          : "bg-gradient-to-br from-slate-100 to-blue-50 text-slate-800"
      }`}
    >
      <div
        className={`max-w-6xl mx-auto rounded-xl shadow-lg p-8 ${
          darkMode ? "bg-slate-900 border border-slate-700" : "bg-white"
        }`}
      >
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold">CureX</h1>
            <p className={`${darkMode ? "text-slate-300" : "text-gray-500"} text-sm`}>
              AI-Powered Lung Disease Detection System
            </p>
          </div>

          <button
            onClick={() => setDarkMode((prev) => !prev)}
            className={`px-4 py-2 rounded-lg text-sm font-semibold ${
              darkMode
                ? "bg-slate-700 text-white"
                : "bg-slate-200 text-slate-800"
            }`}
          >
            {darkMode ? "Light Mode" : "Dark Mode"}
          </button>
        </div>

        <div
          className={`p-3 rounded-lg mb-4 text-sm ${
            darkMode
              ? "bg-yellow-950 border border-yellow-700"
              : "bg-yellow-50 border border-yellow-200"
          }`}
        >
          <strong>Patient:</strong> {patient.name} | Age: {patient.age} | Previous Disease: {patient.previousDisease || "None"}
        </div>

        {getRiskWarning() && (
          <div
            className={`p-3 rounded-lg mb-6 ${
              darkMode
                ? "bg-red-950 border border-red-700 text-red-200"
                : "bg-red-50 border border-red-200 text-red-700"
            }`}
          >
            <strong>Risk Alert:</strong> {getRiskWarning()}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div
            className={`p-6 rounded-xl shadow ${
              darkMode
                ? "bg-emerald-950 border border-emerald-800"
                : "bg-emerald-50 border border-emerald-200"
            }`}
          >
            <form onSubmit={handleSubmit}>
              <input
                type="file"
                name="image"
                accept="image/png,image/jpeg"
                className={`w-full p-3 border-2 border-dashed rounded-lg mb-4 ${
                  darkMode ? "bg-slate-900 border-slate-600" : "bg-gray-50"
                }`}
              />

              <button className="w-full bg-emerald-500 text-white p-3 rounded-lg font-semibold">
                Detect Disease
              </button>
            </form>

            {preview && (
              <div className="mt-5 text-center">
                <img src={preview} className="max-h-64 mx-auto rounded-lg shadow-lg" alt="X-ray preview" />
              </div>
            )}

            {disease && (
              <div className={`mt-6 p-5 rounded-xl border ${darkMode ? "bg-slate-900 border-slate-700" : "bg-white"}`}>
                <h2 className="text-lg font-semibold text-center mb-4">Diagnosis Result</h2>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-xs text-gray-500">Disease</p>
                    <p className="font-bold">{disease}</p>
                  </div>

                  <div>
                    <p className="text-xs text-gray-500">Confidence</p>
                    <p className="font-bold">{numericConfidence}%</p>

                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div
                        className="bg-emerald-500 h-2 rounded-full"
                        style={{ width: `${numericConfidence}%` }}
                      />
                    </div>
                  </div>

                  <div>
                    <p className="text-xs text-gray-500">Severity</p>
                    <p className="font-bold text-red-500">{severity}</p>
                  </div>
                </div>
              </div>
            )}

            {heatmap && (
              <div className="mt-4">
                <button
                  onClick={() => setShowHeatmap((prev) => !prev)}
                  className="w-full bg-violet-600 text-white p-3 rounded-lg font-semibold"
                >
                  {showHeatmap ? "Hide Heatmap" : "Show Heatmap"}
                </button>

                {showHeatmap && (
                  <div className="mt-4 text-center">
                    <img src={heatmap} className="max-h-64 mx-auto rounded-lg shadow-lg" alt="Grad-CAM heatmap" />
                  </div>
                )}
              </div>
            )}

            {disease && (
              <button
                onClick={generatePDF}
                className="mt-5 w-full bg-blue-600 text-white p-3 rounded-lg font-semibold"
              >
                Download Medical Report
              </button>
            )}
          </div>

          <div
            className={`p-6 rounded-xl shadow ${
              darkMode
                ? "bg-slate-800 border border-slate-700"
                : "bg-pink-50 border border-pink-200"
            }`}
          >
            <h2 className="text-xl font-semibold text-center mb-4">Diagnosis Insights</h2>

            {!guidance ? (
              <p className="text-center text-gray-400 mt-10">No results available yet.</p>
            ) : (
              <div
                className="text-sm leading-relaxed mb-6"
                dangerouslySetInnerHTML={{ __html: formatGuidance(guidance) }}
              />
            )}

            <div
              className={`rounded-xl p-4 border ${
                darkMode ? "bg-slate-900 border-slate-700" : "bg-white border-slate-200"
              }`}
            >
              <h3 className="text-lg font-semibold mb-3">Risk Analysis</h3>

              {!riskAnalysis ? (
                <p className="text-sm text-gray-400">Risk analysis will appear after diagnosis.</p>
              ) : (
                <div className="space-y-3 text-sm">
                  <span
                    className={`inline-block px-3 py-1 rounded-full border font-semibold ${riskBadgeClass(
                      riskAnalysis["Risk Level"]
                    )}`}
                  >
                    Risk Level: {riskAnalysis["Risk Level"] || "N/A"}
                  </span>

                  <p>
                    <strong>Age Impact:</strong> {riskAnalysis["Age Impact"] || "N/A"}
                  </p>
                  <p>
                    <strong>Previous Disease Impact:</strong>{" "}
                    {riskAnalysis["Previous Disease Impact"] || "N/A"}
                  </p>
                  <p>
                    <strong>Possible Contribution:</strong>{" "}
                    {riskAnalysis["Possible Contribution"] || "N/A"}
                  </p>

                  <div>
                    <strong>Recommendations:</strong>
                    <ul className="list-disc ml-5 mt-2">
                      {(riskAnalysis.Recommendations || []).map((item, idx) => (
                        <li key={`${item}-${idx}`}>{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
