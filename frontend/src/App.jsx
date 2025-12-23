import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import {
  AlertTriangle,
  CheckCircle,
  Activity,
  ShieldAlert,
} from "lucide-react";
import "./index.css";

const API_URL = "http://localhost:8000/api";

function App() {
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState([]);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [alertsRes, statsRes, reportsRes] = await Promise.all([
          axios.get(`${API_URL}/alerts`),
          axios.get(`${API_URL}/stats`),
          axios.get(`${API_URL}/reports`),
        ]);
        setAlerts(alertsRes.data);
        setStats(statsRes.data);
        setReports(reportsRes.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading)
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900 text-white">
        Loading...
      </div>
    );

  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884d8"];

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 font-sans p-8">
      <header className="mb-10 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
            Fraud Detection Sentinel
          </h1>
          <p className="text-gray-400 mt-2">
            Real-time Transaction Monitoring & Reconciliation
          </p>
        </div>
        <div className="flex items-center space-x-2 bg-gray-800 px-4 py-2 rounded-lg border border-gray-700">
          <div className="h-3 w-3 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm font-medium">System Active</span>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Stat Cards */}
        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-400">Total Fraud Alerts</h3>
            <ShieldAlert className="text-red-500" size={24} />
          </div>
          <p className="text-4xl font-bold">{alerts.length}</p>
        </div>

        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-400">Merchant Categories</h3>
            <Activity className="text-blue-500" size={24} />
          </div>
          <p className="text-4xl font-bold">{stats.length}</p>
        </div>

        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-400">Reconciled Amount</h3>
            <CheckCircle className="text-green-500" size={24} />
          </div>
          <p className="text-4xl font-bold">
            ${reports.length > 0 ? reports[0].validated_amount : "0.00"}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Charts */}
        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 shadow-lg">
          <h2 className="text-xl font-bold mb-6">Fraud by Category</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="merchant_category" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1F2937",
                    borderColor: "#374151",
                    color: "#F3F4F6",
                  }}
                  itemStyle={{ color: "#F3F4F6" }}
                />
                <Bar dataKey="count" fill="#8884d8">
                  {stats.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 shadow-lg">
          <h2 className="text-xl font-bold mb-6">Recent Alerts Feed</h2>
          <div className="overflow-y-auto h-64 pr-2 custom-scrollbar">
            {alerts.length === 0 ? (
              <p className="text-gray-500 text-center py-4">
                No alerts detected yet.
              </p>
            ) : (
              <div className="space-y-3">
                {alerts.map((alert) => (
                  <div
                    key={alert.alert_id}
                    className="bg-gray-800 p-4 rounded-lg border-l-4 border-red-500 flex justify-between items-center"
                  >
                    <div>
                      <p className="font-semibold text-red-400">
                        {alert.fraud_type}
                      </p>
                      <p className="text-sm text-gray-400">
                        {alert.location} • {alert.merchant_category}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-lg">${alert.amount}</p>
                      <p className="text-xs text-gray-500">
                        {new Date(alert.detected_at).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Reports Table */}
      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 shadow-lg">
        <h2 className="text-xl font-bold mb-6">Reconciliation Reports</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-gray-700 text-gray-400 font-medium">
                <p className="py-3 px-4">Report Date</p>
                <p className="py-3 px-4">Total Ingress</p>
                <p className="py-3 px-4">Validated Amount</p>
                <p className="py-3 px-4">Difference</p>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {reports.map((report) => (
                <tr
                  key={report.report_id}
                  className="hover:bg-gray-800 transition-colors"
                >
                  <td className="py-3 px-4">
                    {new Date(report.report_date).toLocaleString()}
                  </td>
                  <td className="py-3 px-4 font-mono">
                    ${report.total_ingress_amount}
                  </td>
                  <td className="py-3 px-4 font-mono text-green-400">
                    ${report.validated_amount}
                  </td>
                  <td className="py-3 px-4 font-mono text-yellow-400">
                    ${report.difference_amount}
                  </td>
                </tr>
              ))}
              {reports.length === 0 && (
                <tr>
                  <td cosSpan="4" className="py-4 text-center text-gray-500">
                    No reports generated yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default App;
