"use client";
import { useEffect, useState } from "react";

const BACKEND_URL = "https://docinfo-5267.onrender.com"; // live backend URL

interface RequestType {
  id: number;
  email: string;
  document: string;
  status: "pending" | "approved" | "rejected";
}

export default function AdminPage() {
  const [requests, setRequests] = useState<RequestType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch all requests
  const fetchRequests = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${BACKEND_URL}/get-requests`);
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      const data = await res.json();
      setRequests(data);
    } catch (err: any) {
      console.error("Failed to fetch requests:", err);
      setError("Failed to load requests. Check your backend or network.");
    } finally {
      setLoading(false);
    }
  };

  // Approve request
  const handleApprove = async (id: number) => {
    try {
      const res = await fetch(`${BACKEND_URL}/approve-request/${id}`, { method: "POST" });
      const data = await res.json();
      alert(data.message || data.error);
      fetchRequests(); // Refresh list
    } catch (err) {
      console.error(err);
      alert("Error approving request!");
    }
  };

  // Reject request
  const handleReject = async (id: number) => {
    try {
      const res = await fetch(`${BACKEND_URL}/reject-request/${id}`, { method: "POST" });
      const data = await res.json();
      alert(data.message || data.error);
      fetchRequests(); // Refresh list
    } catch (err) {
      console.error(err);
      alert("Error rejecting request!");
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  if (loading) return <p style={{ padding: "20px" }}>Loading requests...</p>;
  if (error) return <p style={{ padding: "20px", color: "red" }}>{error}</p>;

  return (
    <div style={{ padding: "30px" }}>
      <h1 style={{ fontSize: "24px", marginBottom: "20px" }}>📂 Document Control Dashboard</h1>

      {requests.length === 0 ? (
        <p>No requests found.</p>
      ) : (
        <table border={1} cellPadding={10}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Email</th>
              <th>Document Name</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {requests.map((req) => (
              <tr key={req.id}>
                <td>{req.id}</td>
                <td>{req.email}</td>
                <td>{req.document}</td>
                <td>{req.status}</td>
                <td>
                  {req.status === "pending" ? (
                    <>
                      <button onClick={() => handleApprove(req.id)}>✅ Approve</button>{" "}
                      <button onClick={() => handleReject(req.id)}>❌ Reject</button>
                    </>
                  ) : (
                    <span>—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
