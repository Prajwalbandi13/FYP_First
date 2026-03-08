import React, { useState } from "react";

function PatientForm({ onSubmit }) {

  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [previousDisease, setPreviousDisease] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!name || !age) {
      alert("Please enter patient name and age");
      return;
    }

    onSubmit({
      name,
      age,
      previousDisease
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-100 to-blue-50">

      <div className="bg-white p-8 rounded-xl shadow-lg w-[400px]">

        <h2 className="text-2xl font-bold text-center mb-6">
          Patient Information
        </h2>

        <form onSubmit={handleSubmit}>

          <input
            type="text"
            placeholder="Patient Name"
            className="w-full p-3 border rounded-lg mb-4"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          <input
            type="number"
            placeholder="Age"
            className="w-full p-3 border rounded-lg mb-4"
            value={age}
            onChange={(e) => setAge(e.target.value)}
          />

          <input
            type="text"
            placeholder="Previous Disease (optional)"
            className="w-full p-3 border rounded-lg mb-6"
            value={previousDisease}
            onChange={(e) => setPreviousDisease(e.target.value)}
          />

          <button
            type="submit"
            className="w-full bg-emerald-500 text-white p-3 rounded-lg font-semibold hover:bg-emerald-600"
          >
            Continue to Diagnosis
          </button>

        </form>

      </div>

    </div>
  );
}

export default PatientForm;