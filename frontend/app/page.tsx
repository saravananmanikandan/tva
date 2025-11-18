"use client";

import { useState, useEffect } from "react";
import axios from "axios";

const AGENT = "https://traffic-agent-615548009762.us-central1.run.app";

export default function Dashboard() {
  // Dashboard Data
  const [violations, setViolations] = useState<any[]>([]);
  const [loadingViolations, setLoadingViolations] = useState(true);

  // Upload Section
  const [imageUrl, setImageUrl] = useState("");
  const [analysis, setAnalysis] = useState<any>(null);
  const [uploadLoading, setUploadLoading] = useState(false);

  // Dummy users
  const [userForm, setUserForm] = useState({ name: "", plate: "", email: "" });
  const [userMsg, setUserMsg] = useState("");

  // Load violations from backend
  useEffect(() => {
    const load = async () => {
      try {
        const res = await axios.get("https://traffic-agent-615548009762.us-central1.run.app/violations");
        console.log(res)
        setViolations(res.data.violations || []);
      } catch (e) {
        console.error(e);
      }
      setLoadingViolations(false);
    };
    load();
  }, []);

  // Handle upload → analyze
  const analyzeImage = async () => {
    console.log("Analyze Image is clicked")
    try {
      setUploadLoading(true);
    console.log("Analyze Image is in try block")

      const res = await axios.post("https://traffic-agent-615548009762.us-central1.run.app/analyze_url", { url: imageUrl });
      setAnalysis(res.data.vision_result);
    } catch (e: any) {
      setAnalysis({ error: e.message });
    }
    setUploadLoading(false);
  };

  // Handle add user
  const handleUserSubmit = async () => {
    try {
      await axios.post(`${AGENT}/register_user`, userForm);
      setUserMsg("User added successfully!");
      setUserForm({ name: "", plate: "", email: "" });
    } catch (e) {
      setUserMsg("Failed to add user.");
    }
  };

  return (
    <div className="p-6 space-y-12">

      {/* HEADER */}
      <header className="bg-white p-5 rounded-xl shadow flex justify-between items-center">
        <h1 className="text-3xl font-bold">Tva Traffic Dashboard</h1>
        <p className="text-gray-600">AI Powered Violation Detection</p>
      </header>

      {/* =======================
          SECTION 1 — VIOLATIONS GRID
      ======================== */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Recent Violations</h2>

        {loadingViolations ? (
          <p className="text-gray-500">Loading violations...</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {violations.map((v, i) => (
              <div key={i} className="p-4 bg-white shadow rounded-xl border">

                <p className="font-bold text-lg">Plate: {v.number_plate || "Unknown"}</p>
                <p className="text-gray-600 text-sm mt-1">{v.summary}</p>

                <div className="mt-3 text-sm grid grid-cols-2 gap-2">
                  {Object.entries(v)
                    .filter(([key]) => key.includes("_violation"))
                    .map(([key, value]) => (
                      <p
                        key={key}
                        className={value ? "text-red-600" : "text-green-600"}
                      >
                        {key.replace("_", " ")}: {value ? "Yes" : "No"}
                      </p>
                    ))}
                </div>
              </div>
            ))}

            {violations.length === 0 && (
              <p className="text-gray-500">No violations logged yet.</p>
            )}
          </div>
        )}
      </section>

      {/* =======================
          SECTION 2 — UPLOAD & ANALYZE
      ======================== */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Upload Image for Analysis</h2>

        <div className="bg-white p-6 rounded-xl shadow max-w-xl space-y-3 border">

          <input
            type="text"
            placeholder="Paste image URL..."
            value={imageUrl}
            onChange={(e) => setImageUrl(e.target.value)}
            className="border px-3 py-2 rounded w-full"
          />

          <button
            onClick={analyzeImage}
            disabled={uploadLoading}
            className="bg-blue-600 text-white px-4 py-2 rounded w-full"
          >
            {uploadLoading ? "Analyzing..." : "Analyze Image"}
          </button>

          {analysis && (
            <pre className="bg-gray-100 p-3 rounded overflow-x-auto text-sm">
              {JSON.stringify(analysis, null, 2)}
            </pre>
          )}
        </div>
      </section>

      {/* =======================
          SECTION 3 — ADD USER
      ======================== */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Add Dummy User</h2>

        <div className="bg-white p-6 rounded-xl shadow max-w-lg border space-y-4">

          <input
            className="border p-2 rounded w-full"
            placeholder="Name"
            value={userForm.name}
            onChange={(e) => setUserForm({ ...userForm, name: e.target.value })}
          />

          <input
            className="border p-2 rounded w-full"
            placeholder="License Plate"
            value={userForm.plate}
            onChange={(e) => setUserForm({ ...userForm, plate: e.target.value })}
          />

          <input
            className="border p-2 rounded w-full"
            placeholder="Email"
            value={userForm.email}
            onChange={(e) => setUserForm({ ...userForm, email: e.target.value })}
          />

          <button
            onClick={handleUserSubmit}
            className="bg-green-600 text-white px-4 py-2 rounded w-full"
          >
            Save User
          </button>

          {userMsg && <p className="text-green-700">{userMsg}</p>}
        </div>
      </section>
    </div>
  );
}
