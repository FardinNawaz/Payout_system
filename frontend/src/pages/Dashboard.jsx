import { useEffect, useState } from "react";
import axios from "axios";

import {
  Building2,
  Users,
  UserRoundCheck,
  ArrowLeftRight,
  CheckCircle,
  XCircle,
  Clock
} from "lucide-react";

import "./Dashboard.css";

function Dashboard() {

  const [summary, setSummary] = useState(null);
  const [payoutStats, setPayoutStats] = useState(null);
  const [recentPayouts, setRecentPayouts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchSummary = async () => {
        try {
            const token = localStorage.getItem("access_token");

            const response = await axios.get(
                "http://127.0.0.1:8000/api/v1/admin/dashboard/summary",
                {
                    headers: {
                        access_token: token
                    }
                }
            );

            console.log("Dashboard data:", response.data);
            setSummary(response.data.data);

        } catch (error) {
            console.log("Error message:", error.message);
            console.log("Status code:", error.response?.status);
            console.log("Backend error:", error.response?.data);

            setError(
                error.response?.data?.detail ||
                "Unable to load dashboard summary."
            );

        } finally {
            setLoading(false);
        }
    };
    const fetchPayoutStats = async () => {
        try {
            const token = localStorage.getItem("access_token");

            const response = await axios.get(
            "http://127.0.0.1:8000/api/v1/admin/dashboard/payout-stats",
            {
                headers: {
                access_token: token
                }
            }
            );

            console.log("Payout statistics:", response.data);

            setPayoutStats(response.data.data);

        } catch (error) {
            console.log("Payout statistics error:", error.response?.data || error.message);
        
        }finally {
        console.log("Payout statistics API request completed");
        }
        };
    const fetchRecentPayouts = async () => {
    try {
        const token = localStorage.getItem("access_token");

        const response = await axios.get(
        "http://127.0.0.1:8000/api/v1/admin/dashboard/recent-payouts",
        {
            headers: {
            access_token: token
            }
        }
        );

        console.log("Recent payouts:", response.data);

        setRecentPayouts(response.data.data);

    } catch (error) {
        console.log(
        "Recent payouts error:",
        error.response?.data || error.message
        );
    }
    };
            
    fetchSummary();
    fetchPayoutStats();
    fetchRecentPayouts();

  }, []);

  const cards = [
    {
      title: "Total Organizations",
      value: summary?.total_organizations ?? 0,
      icon: Building2,
      color: "blue"
    },
    {
      title: "Total Remitters",
      value: summary?.total_remitters ?? 0,
      icon: Users,
      color: "purple"
    },
    {
      title: "Total Beneficiaries",
      value: summary?.total_beneficiaries ?? 0,
      icon: UserRoundCheck,
      color: "teal"
    },
    {
      title: "Total Payouts",
      value: summary?.total_payouts ?? 0,
      icon: ArrowLeftRight,
      color: "orange"
    },
    {
      title: "Successful Payouts",
      value: summary?.successful_payouts ?? 0,
      icon: CheckCircle,
      color: "green"
    },
    {
      title: "Failed Payouts",
      value: summary?.failed_payouts ?? 0,
      icon: XCircle,
      color: "red"
    },
    {
      title: "Pending Payouts",
      value: summary?.pending_payouts ?? 0,
      icon: Clock,
      color: "yellow"
    }
  ];
  if (loading) {
    return <div className="dashboard-content">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard-content">

      <div className="dashboard-heading">
        <h1>Dashboard Overview</h1>
        <p>Welcome to LeoPay Admin Panel</p>
      </div>

      {error && <p className="error-message">{error}</p>}

      {/* Summary Cards */}
      <div className="summary-grid">
        {cards.map((card) => {
          const Icon = card.icon;

          return (
            <div className="summary-card" key={card.title}>
              <div className={`card-icon ${card.color}`}>
                <Icon size={24} />
              </div>

              <div className="card-info">
                <p>{card.title}</p>
                <h2>{card.value}</h2>
              </div>
            </div>
          );
        })}
      </div>

      {/* Payout Statistics */}
      <div className="payout-stats-section">
        <h2>Payout Statistics</h2>

        <div className="payout-stats-grid">

          <div className="payout-stat-card">
            <p>Total Payout Amount</p>
            <h3>
              ₹{Number(payoutStats?.total_amount ?? 0).toLocaleString("en-IN")}
            </h3>
          </div>

          <div className="payout-stat-card success">
            <p>Successful Amount</p>
            <h3>
              ₹{Number(payoutStats?.successful_amount ?? 0).toLocaleString("en-IN")}
            </h3>
          </div>

          <div className="payout-stat-card failed">
            <p>Failed Amount</p>
            <h3>
              ₹{Number(payoutStats?.failed_amount ?? 0).toLocaleString("en-IN")}
            </h3>
          </div>

          <div className="payout-stat-card pending">
            <p>Pending Amount</p>
            <h3>
              ₹{Number(payoutStats?.pending_amount ?? 0).toLocaleString("en-IN")}
            </h3>
          </div>

        </div>
      </div>
      {/* Recent Payouts */}
    <div className="recent-payouts-section">

    <h2>Recent Payouts</h2>

    <div className="table-container">

        <table className="payout-table">

        <thead>
            <tr>
            <th>Payout ID</th>
            <th>Amount</th>
            <th>Currency</th>
            <th>Payment Mode</th>
            <th>Status</th>
            <th>Created At</th>
            </tr>
        </thead>

        <tbody>
            {recentPayouts.length > 0 ? (
            recentPayouts.map((payout) => (
                <tr key={payout.payout_id}>

                <td>{payout.payout_id}</td>

                <td>
                    {Number(payout.amount).toLocaleString("en-IN")}
                </td>

                <td>{payout.currency}</td>

                <td>{payout.payment_mode}</td>

                <td>
                    <span className={`status-badge ${payout.status?.toLowerCase()}`}>
                    {payout.status}
                    </span>
                </td>

                <td>
                    {payout.created_at
                    ? new Date(payout.created_at).toLocaleString("en-IN")
                    : "-"}
                </td>

                </tr>
            ))
            ) : (
            <tr>
                <td colSpan="6">No recent payouts found.</td>
            </tr>
            )}
        </tbody>

        </table>

    </div>

    </div>

    </div>
  );
}

export default Dashboard;