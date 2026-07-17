import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, ArcElement, BarElement, Title, Tooltip, Legend, Filler } from 'chart.js';
import { Shield, Upload, AlertTriangle, TrendingUp, ScanSearch, ChevronRight, Activity } from 'lucide-react';
import { dashboardAPI } from '../utils/api';
import { getRiskColor, getRiskBg } from '../utils/helpers';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, ArcElement, BarElement, Title, Tooltip, Legend, Filler);

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardAPI.get().then(res => setStats(res.data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <DashboardSkeleton />;
  if (!stats) return <div className="text-center py-20 text-gray-500">Failed to load dashboard data.</div>;

  const riskTrendData = {
    labels: stats.risk_trend?.map(d => d.date) || [],
    datasets: [{
      label: 'Risk Score',
      data: stats.risk_trend?.map(d => d.score) || [],
      borderColor: '#338dff',
      backgroundColor: 'rgba(51, 141, 255, 0.1)',
      fill: true,
      tension: 0.4,
      pointRadius: 2,
      pointHoverRadius: 6,
    }],
  };

  const portDistData = {
    labels: stats.port_distribution?.map(d => d.level) || [],
    datasets: [{
      data: stats.port_distribution?.map(d => d.count) || [],
      backgroundColor: ['#dc2626', '#ea580c', '#d97706', '#16a34a'],
      borderWidth: 0,
    }],
  };

  const scanTypeData = {
    labels: stats.scan_type_distribution?.map(d => d.type) || [],
    datasets: [{
      label: 'Scans',
      data: stats.scan_type_distribution?.map(d => d.count) || [],
      backgroundColor: ['#338dff', '#10b981', '#f59e0b', '#8b5cf6'],
      borderRadius: 6,
    }],
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">Network security overview</p>
        </div>
        <Link to="/scans/upload" className="btn-primary flex items-center gap-2">
          <Upload size={16} /> New Scan
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Total Scans', value: stats.total_scans, icon: ScanSearch, color: 'text-primary-500', bg: 'bg-primary-500/10' },
          { label: 'Avg Risk Score', value: stats.avg_risk_score, icon: Shield, color: getRiskColor(stats.avg_risk_score), bg: getRiskBg(stats.avg_risk_score) },
          { label: 'Open Ports Found', value: stats.total_open_ports, icon: Activity, color: 'text-blue-500', bg: 'bg-blue-500/10' },
          { label: 'Critical Findings', value: stats.critical_findings, icon: AlertTriangle, color: stats.critical_findings > 0 ? 'text-red-500' : 'text-green-500', bg: stats.critical_findings > 0 ? 'bg-red-500/10' : 'bg-green-500/10' },
        ].map(({ label, value, icon: Icon, color, bg }) => (
          <div key={label} className="card p-5">
            <div className="flex items-center gap-3 mb-3">
              <div className={`w-10 h-10 ${bg} rounded-lg flex items-center justify-center`}>
                <Icon size={20} className={color} />
              </div>
              <span className="text-sm text-gray-500">{label}</span>
            </div>
            <div className="text-3xl font-bold">{value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card p-5 lg:col-span-2">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <TrendingUp size={18} className="text-primary-500" /> Risk Score Trend (30 Days)
          </h3>
          <div className="h-64">
            <Line data={riskTrendData} options={{
              responsive: true, maintainAspectRatio: false,
              plugins: { legend: { display: false } },
              scales: {
                y: { beginAtZero: true, max: 100, grid: { color: 'rgba(128,128,128,0.1)' } },
                x: { grid: { display: false }, ticks: { maxTicksLimit: 10 } },
              },
            }} />
          </div>
        </div>

        <div className="card p-5">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Shield size={18} className="text-primary-500" /> Risk Distribution
          </h3>
          <div className="h-64 flex items-center justify-center">
            {stats.port_distribution?.some(d => d.count > 0) ? (
              <Doughnut data={portDistData} options={{
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { padding: 12, usePointStyle: true } } },
                cutout: '65%',
              }} />
            ) : (
              <p className="text-gray-400 text-sm">No data yet</p>
            )}
          </div>
        </div>
      </div>

      {stats.scan_type_distribution?.length > 0 && (
        <div className="card p-5">
          <h3 className="font-semibold mb-4">Scan Types</h3>
          <div className="h-48">
            <Bar data={scanTypeData} options={{
              responsive: true, maintainAspectRatio: false,
              plugins: { legend: { display: false } },
              scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } }, x: { grid: { display: false } } },
            }} />
          </div>
        </div>
      )}

      <div className="card">
        <div className="p-5 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
          <h3 className="font-semibold">Recent Scans</h3>
          <Link to="/scans" className="text-sm text-primary-500 hover:text-primary-600 flex items-center gap-1">
            View All <ChevronRight size={14} />
          </Link>
        </div>
        <div className="divide-y divide-gray-100 dark:divide-gray-800">
          {stats.recent_scans?.length > 0 ? stats.recent_scans.map(scan => (
            <Link key={scan.id} to={`/scans/${scan.id}`} className="flex items-center gap-4 p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold ${getRiskBg(scan.risk_score)} ${getRiskColor(scan.risk_score)}`}>
                {scan.risk_score}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">{scan.title}</p>
                <p className="text-sm text-gray-500 truncate">{scan.target} — {scan.open_ports} open ports</p>
              </div>
              <div className="text-right">
                <span className={`badge ${scan.status === 'completed' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'}`}>
                  {scan.status}
                </span>
                <p className="text-xs text-gray-400 mt-1">{new Date(scan.created_at).toLocaleDateString()}</p>
              </div>
            </Link>
          )) : (
            <div className="p-8 text-center text-gray-400">
              <p>No scans yet.</p>
              <Link to="/scans/upload" className="text-primary-500 hover:text-primary-600 text-sm mt-2 inline-block">Upload your first scan →</Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-8 bg-gray-200 dark:bg-gray-800 rounded w-48" />
      <div className="grid grid-cols-4 gap-4">
        {[1,2,3,4].map(i => <div key={i} className="card p-5 h-28 bg-gray-100 dark:bg-gray-800/50" />)}
      </div>
      <div className="grid grid-cols-3 gap-6">
        <div className="card h-72 col-span-2 bg-gray-100 dark:bg-gray-800/50" />
        <div className="card h-72 bg-gray-100 dark:bg-gray-800/50" />
      </div>
    </div>
  );
}
