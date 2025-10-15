"use client";

import { useState } from "react";

export default function Home() {
  const [email, setEmail] = useState("");
  const [documentName, setDocumentName] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage("Submitting...");

    try {
      const res = await fetch("https://docinfo-backend.onrender.com/request-document", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          document_name: documentName,
        }),
      });

      const data = await res.json();
      if (res.ok) {
        setMessage("✅ Request submitted successfully!");
      } else {
        setMessage("❌ Failed: " + data.error);
      }
    } catch (err) {
      setMessage("⚠️ Error connecting to backend!");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <h1 className="text-3xl font-bold mb-6">📄 Request a Document</h1>

      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-2xl shadow-md w-96">
        <div className="mb-4">
          <label className="block mb-2 font-semibold">Your Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full border p-2 rounded-md"
          />
        </div>

        <div className="mb-4">
          <label className="block mb-2 font-semibold">Document Name</label>
          <input
            type="text"
            value={documentName}
            onChange={(e) => setDocumentName(e.target.value)}
            required
            className="w-full border p-2 rounded-md"
          />
        </div>

        <button
          type="submit"
          className="bg-blue-600 text-white w-full py-2 rounded-md hover:bg-blue-700 transition"
        >
          Submit Request
        </button>
      </form>

      {message && <p className="mt-4 text-gray-700">{message}</p>}
    </div>
  );
}
