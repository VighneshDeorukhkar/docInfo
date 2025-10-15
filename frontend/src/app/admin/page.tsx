"use client";
import { useEffect, useState } from "react";

export default function AdminPage() {
  const [requests, setRequests] = useState([]);

  const fetchRequests = async () => {
    const res = await fetch("http://127.0.0.1:5000/get-requests");
    const data = await res.json();
    setRequests(data);
  };

  const handleApprove = async (id: number) => {
    const res = await fetch(`http://127.0.0.1:5000/approve-request/${id}`, {
      method: "POST",
    });
    const data = await res.json();
    alert(data.message || data.error);
    fetchRequests();
  };

  const handleReject = async (id: number) => {
    const res = await fetch(`http://127.0.0.1:5000/reject-request/${id}`, {
      method: "POST",
    });
    const data = await res.json();
    alert(data.message || data.error);
    fetchRequests();
  };

  useEffect(() => {
    fetchRequests();
  }, []);

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
                  {req.status === "pending" && (
                    <>
                      <button onClick={() => handleApprove(req.id)}>✅ Approve</button>{" "}
                      <button onClick={() => handleReject(req.id)}>❌ Reject</button>
                    </>
                  )}
                  {req.status !== "pending" && <span>—</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
