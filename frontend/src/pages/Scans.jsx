import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { scanAPI } from '../utils/api';
import { getRiskColor, getRiskBg, getRiskLabel } from '../utils/helpers';
import { ScanSearch, Upload, Trash2, ExternalLink, Filter } from 'lucide-react';
import toast from 'react-hot-toast';

export default function Scans() {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => { loadScans(); }, []);

  const loadScans = () => {
    scanAPI.list().then(res => setScans(res.data)).catch(() => toast.error('Failed to load scans')).finally(() => setLoading(false));
  };

  const deleteScan = async (id, e) => {
    e.preventDefault();
    if (!confirm('Delete this scan?')) return;
    try {
      await scanAPI.delete(id);
      setScans(scans.filter(s => s.id !== id));
      toast.success('Scan deleted');
    } catch { toast.error('Failed to delete'); }
  };

  const filtered = scans.filter(s => {
    if (filter === 'all') return true;
    if (filter === 'critical') return s.risk_score >= 80;
    if (filter === 'high') return s.risk_score >= 60 && s.risk_score < 80;
    if (filter === 'completed') return s.status === 'completed';
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Scan History</h1>
          <p className="text-sm text-gray-500 mt-1">{scans.length} scans total</p>
        </div>
        <Link to="/scans/upload" className="btn-primary flex items-center gap-2">
          <Upload size={16} /> New Scan
        </Link>
      </div>

      <div className="flex items-center gap-2 flex-wrap">
        {['all', 'critical', 'high', 'completed'].map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${filter === f ? 'bg-primary-600 text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'}`}>
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-3">
          {[1,2,3].map(i => <div key={i} className="card h-24 animate-pulse bg-gray-100 dark:bg-gray-800/50" />)}
        </div>
      ) : filtered.length === 0 ? (
        <div className="card p-12 text-center">
          <ScanSearch size={48} className="mx-auto text-gray-300 dark:text-gray-600 mb-4" />
          <p className="text-gray-500 mb-4">No scans found</p>
          <Link to="/scans/upload" className="btn-primary inline-flex items-center gap-2">
            <Upload size={16} /> Upload Your First Scan
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map(scan => (
            <Link key={scan.id} to={`/scans/${scan.id}`} className="card p-5 flex items-center gap-5 hover:shadow-md transition-all group">
              <div className={`w-14 h-14 rounded-xl flex flex-col items-center justify-center ${getRiskBg(scan.risk_score)} flex-shrink-0`}>
                <span className={`text-lg font-bold ${getRiskColor(scan.risk_score)}`}>{scan.risk_score}</span>
                <span className={`text-[9px] font-bold uppercase ${getRiskColor(scan.risk_score)}`}>{getRiskLabel(scan.risk_score)}</span>
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-semibold truncate">{scan.title}</h3>
                  <span className={`badge text-[10px] ${scan.status === 'completed' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : scan.status === 'processing' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'}`}>
                    {scan.status}
                  </span>
                </div>
                <p className="text-sm text-gray-500 truncate">{scan.target}</p>
                <div className="flex items-center gap-4 mt-1.5 text-xs text-gray-400">
                  <span>{scan.open_ports} open ports</span>
                  <span>{scan.total_ports} scanned</span>
                  <span className="uppercase font-medium text-primary-500">{scan.scan_type}</span>
                  <span>{new Date(scan.created_at).toLocaleDateString()}</span>
                </div>
              </div>

              <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button onClick={(e) => deleteScan(scan.id, e)} className="p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-gray-400 hover:text-red-500 transition-colors" title="Delete">
                  <Trash2 size={16} />
                </button>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
