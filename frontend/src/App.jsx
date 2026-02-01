import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
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
  Upload,
  RefreshCw,
  FileText,
} from "lucide-react";
import "./index.css";

const API_URL = "http://localhost:8000/api";

function App() {
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState([]);
  const [reports, setReports] = useState([]);
  const [fraudTypes, setFraudTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      const [alertsRes, statsRes, reportsRes, typesRes] = await Promise.all([
        axios.get(`${API_URL}/alerts`),
        axios.get(`${API_URL}/stats`),
        axios.get(`${API_URL}/reports`),
        axios.get(`${API_URL}/fraud-types`),
      ]);
      setAlerts(alertsRes.data);
      setStats(statsRes.data);
      setReports(reportsRes.data);
      setFraudTypes(typesRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    setUploadResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setUploadResult({
        success: true,
        message: `Successfully sent ${response.data.transactions_sent} transactions`,
      });
      setTimeout(fetchData, 2000); // Refresh data after upload
    } catch (error) {
      setUploadResult({
        success: false,
        message: error.response?.data?.detail || "Upload failed",
      });
    } finally {
      setUploading(false);
    }
  };

  if (loading)
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900 text-white">
        <RefreshCw className="animate-spin mr-2" /> Loading...
      </div>
    );

  const COLORS = ["#EF4444", "#3B82F6", "#10B981", "#F59E0B", "#8B5CF6"];

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
        <div className="flex items-center space-x-4">
          {/* File Upload */}
          <label className="cursor-pointer bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium py-2 px-4 rounded-lg flex items-center space-x-2 transition-all">
            <Upload size={18} />
            <span>{uploading ? "Uploading..." : "Upload CSV"}</span>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              className="hidden"
              disabled={uploading}
            />
          </label>
          <div className="flex items-center space-x-2 bg-gray-800 px-4 py-2 rounded-lg border border-gray-700">
            <div className="h-3 w-3 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium">System Active</span>
          </div>
        </div>
      </header>

      {/* Upload Result Message */}
      {uploadResult && (
        <div
          className={`mb-6 p-4 rounded-lg flex items-center space-x-2 ${
            uploadResult.success
              ? "bg-green-900/30 border border-green-700 text-green-400"
              : "bg-red-900/30 border border-red-700 text-red-400"
          }`}
        >
          {uploadResult.success ? (
            <CheckCircle size={20} />
          ) : (
            <AlertTriangle size={20} />
          )}
          <span>{uploadResult.message}</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
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
            <h3 className="text-gray-400">High Value Frauds</h3>
            <AlertTriangle className="text-yellow-500" size={24} />
          </div>
          <p className="text-4xl font-bold">
            {fraudTypes.find((t) => t.fraud_type === "High Value")?.count || 0}
          </p>
        </div>

        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-400">Impossible Travel</h3>
            <Activity className="text-blue-500" size={24} />
          </div>
          <p className="text-4xl font-bold">
            {fraudTypes.find((t) => t.fraud_type === "Impossible Travel")
              ?.count || 0}
          </p>
        </div>

        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-400">Reconciled Amount</h3>
            <CheckCircle className="text-green-500" size={24} />
          </div>
          <p className="text-4xl font-bold">
            ${reports.length > 0 ? reports[0].validated_amount?.toFixed(2) : "0.00"}
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
          <h2 className="text-xl font-bold mb-6">Fraud Type Distribution</h2>
          <div className="h-64 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={fraudTypes}
                  dataKey="count"
                  nameKey="fraud_type"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ fraud_type, count }) => `${fraud_type}: ${count}`}
                >
                  {fraudTypes.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1F2937",
                    borderColor: "#374151",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Alerts Feed */}
      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 shadow-lg mb-8">
        <h2 className="text-xl font-bold mb-6 flex items-center">
          <AlertTriangle className="text-red-500 mr-2" size={20} />
          Recent Fraud Alerts
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-gray-700 text-gray-400 font-medium">
                <th className="py-3 px-4">Time</th>
                <th className="py-3 px-4">User</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Amount</th>
                <th className="py-3 px-4">Location</th>
                <th className="py-3 px-4">Category</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {alerts.slice(0, 10).map((alert) => (
                <tr
                  key={alert.alert_id}
                  className="hover:bg-gray-800 transition-colors"
                >
                  <td className="py-3 px-4 text-gray-400">
                    {new Date(alert.detected_at).toLocaleTimeString()}
                  </td>
                  <td className="py-3 px-4 font-mono">{alert.user_id}</td>
                  <td className="py-3 px-4">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        alert.fraud_type === "High Value"
                          ? "bg-yellow-900/50 text-yellow-400"
                          : "bg-blue-900/50 text-blue-400"
                      }`}
                    >
                      {alert.fraud_type}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono text-red-400">
                    ${alert.amount?.toFixed(2)}
                  </td>
                  <td className="py-3 px-4">{alert.location}</td>
                  <td className="py-3 px-4">{alert.merchant_category}</td>
                </tr>
              ))}
              {alerts.length === 0 && (
                <tr>
                  <td colSpan="6" className="py-4 text-center text-gray-500">
                    No alerts detected yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* CSV Format Helper */}
      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 shadow-lg">
        <h2 className="text-xl font-bold mb-4 flex items-center">
          <FileText className="text-purple-500 mr-2" size={20} />
          CSV Upload Format
        </h2>
        <p className="text-gray-400 mb-4">
          Upload a CSV file with the following columns to inject transactions:
        </p>
        <div className="bg-gray-800 p-4 rounded-lg font-mono text-sm overflow-x-auto">
          <p className="text-gray-300">user_id,merchant_category,amount,location,country</p>
          <p className="text-gray-500">user_1,Electronics,7500.00,New York,USA</p>
          <p className="text-gray-500">user_2,Travel,250.00,London,UK</p>
        </div>
      </div>
    </div>
  );
}

export default App;
