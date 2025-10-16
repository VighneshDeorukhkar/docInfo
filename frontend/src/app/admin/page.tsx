"use client";
import { useEffect, useState } from "react";

const BACKEND_URL = "https://docinfo-5267.onrender.com"; // your live backend

export default function AdminPage() {
  const [requests, setRequests] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch all requests from backend
  const fetchRequests = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/get-requests`);
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      const data = await res.json();
      setRequests(data);
    } catch (err) {
      console.error("Failed to fetch requests:", err);
    } finally {
      setLoading(false);
    }
  };

  // Approve request
  const handleApprove = async (id: number) => {
    try {
      const res = await fetch(`${BACKEND_URL}/approve-request/${id}`, {
        method: "POST",
      });
      const data = await res.json();
      alert(data.message || data.error);
      fetchRequests();
    } catch (err) {
      console.error(err);
      alert("Error approving request!");
    }
  };

  // Reject request
  const handleReject = async (id: number) => {
    try {
      const res = await fetch(`${BACKEND_URL}/reject-request/${id}`, {
        method: "POST",
      });
      const data = await res.json();
      alert(data.message || data.error);
      fetchRequests();
    } catch (err) {
      console.error(err);
      alert("Error rejecting request!");
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  if (loading) return <p style={{ padding: "20px" }}>Loading requests...</p>;

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
            {requests.map((req: any) => (
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
