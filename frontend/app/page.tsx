"use client";

import { useState, useEffect } from "react";
import axios from "axios";

const AGENT = "https://traffic-agent-615548009762.us-central1.run.app";

export default function Dashboard() {
  const [violations, setViolations] = useState<any[]>([]);
  const [loadingViolations, setLoadingViolations] = useState(true);
  const [imageUrl, setImageUrl] = useState("");
  const [analysis, setAnalysis] = useState<any>(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [userForm, setUserForm] = useState({ name: "", plate: "", email: "" });
  const [userMsg, setUserMsg] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const res = await axios.get(`${AGENT}/violations`);
        setViolations(res.data.violations || []);
      } catch (e) {
        console.error(e);
      }
      setLoadingViolations(false);
    };
    load();
  }, []);

  const analyzeImage = async () => {
    try {
      setUploadLoading(true);
      const res = await axios.post(`${AGENT}/analyze_url`, { url: imageUrl });
      setAnalysis(res.data.vision_result);
    } catch (e: any) {
      setAnalysis({ error: e.message });
    }
    setUploadLoading(false);
  };

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
    <div className="min-h-screen bg-gray-100 text-gray-900">
      
      {/* NAVBAR */}
      <nav className="bg-white shadow-md px-6 py-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold">🛣️ TVA Dashboard</h1>
        <div className="flex gap-3">
          <button className="p-2 rounded-lg bg-gray-200 hover:bg-gray-300">⚙️</button>
          <button className="p-2 rounded-lg bg-gray-200 hover:bg-gray-300">🔔</button>
          <div className="size-10 rounded-full bg-gray-300" />
        </div>
      </nav>

      {/* PAGE CONTAINER */}
      <main className="p-6 max-w-7xl mx-auto">
        <h2 className="text-3xl font-extrabold mb-6">Traffic Violation Dashboard</h2>

        {/* GRID LAYOUT */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* VIOLATIONS TABLE */}
          <section className="lg:col-span-2 bg-white p-6 rounded-xl shadow-md">
            <h3 className="text-xl font-bold mb-4">Recent Violations</h3>

            {loadingViolations ? (
              <p>Loading violations...</p>
            ) : violations.length === 0 ? (
              <p>No violations found.</p>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="py-2 text-left">Plate</th>
                    <th className="py-2 text-left">Summary</th>
                    <th className="py-2 text-left">Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {violations.map((v, i) => (
                    <tr key={i} className="border-b hover:bg-gray-50">
                      <td className="py-2">{v.number_plate}</td>
                      <td className="py-2">{v.summary}</td>
                      <td>
                        <span
                          className={`px-2 py-1 rounded-full text-white text-xs
                          ${v.severity_score > 2 ? "bg-red-500" : "bg-yellow-500"}`}
                        >
                          {v.severity_score}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>

          {/* SIDE PANEL */}
          <div className="flex flex-col gap-6">
            
            {/* UPLOAD IMAGE */}
            <section className="bg-white p-6 rounded-xl shadow-md">
              <h3 className="text-xl font-bold mb-4">Analyze Image</h3>
              <input
                type="text"
                placeholder="Enter image URL..."
                value={imageUrl}
                onChange={(e) => setImageUrl(e.target.value)}
                className="border rounded w-full p-2"
              />
              <button
                onClick={analyzeImage}
                className="mt-3 w-full py-2 rounded bg-blue-600 text-white hover:bg-blue-700"
              >
                {uploadLoading ? "Analyzing..." : "Analyze"}
              </button>

              {analysis && (
                <pre className="mt-4 bg-gray-100 p-3 rounded text-xs">
                  {JSON.stringify(analysis, null, 2)}
                </pre>
              )}
            </section>

            {/* ADD USER FORM */}
            <section className="bg-white p-6 rounded-xl shadow-md">
              <h3 className="text-xl font-bold mb-4">Add User</h3>

              {["name", "plate", "email"].map((field) => (
                <input
                  key={field}
                  placeholder={field.toUpperCase()}
                  value={userForm[field as keyof typeof userForm]}
                  onChange={(e) => setUserForm({ ...userForm, [field]: e.target.value })}
                  className="border rounded w-full p-2 mb-2"
                />
              ))}

              <button
                onClick={handleUserSubmit}
                className="w-full py-2 rounded bg-green-600 text-white hover:bg-green-700"
              >
                Save User
              </button>

              {userMsg && <p className="text-green-700 text-sm mt-2">{userMsg}</p>}
            </section>
          </div>
        </div>
      </main>
    </div>
  );
}
