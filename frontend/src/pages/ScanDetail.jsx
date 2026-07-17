import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { scanAPI } from '../utils/api';
import { getRiskColor, getRiskBg, getRiskLabel, getRiskBadge } from '../utils/helpers';
import { ArrowLeft, Download, Brain, Shield, AlertTriangle, CheckCircle, MessageSquare, Send, ExternalLink, Globe, Clock, FileText } from 'lucide-react';
import toast from 'react-hot-toast';

export default function ScanDetail() {
  const { id } = useParams();
  const [scan, setScan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    scanAPI.get(id).then(res => setScan(res.data)).catch(() => toast.error('Failed to load scan')).finally(() => setLoading(false));
    scanAPI.listComments(id).then(res => setComments(res.data)).catch(() => {});
  }, [id]);

  const addComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    try {
      const res = await scanAPI.addComment(id, { content: newComment });
      setComments([...comments, res.data]);
      setNewComment('');
    } catch { toast.error('Failed to add comment'); }
  };

  if (loading) return <ScanDetailSkeleton />;
  if (!scan) return <div className="text-center py-20 text-gray-500">Scan not found.</div>;

  const openPorts = scan.ports?.filter(p => p.state === 'open') || [];
  const closedPorts = scan.ports?.filter(p => p.state === 'closed') || [];
  const filteredPorts = scan.ports?.filter(p => p.state === 'filtered') || [];

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Shield },
    { id: 'ports', label: `Ports (${openPorts.length})`, icon: Globe },
    { id: 'recommendations', label: 'Recommendations', icon: AlertTriangle },
    { id: 'comments', label: `Comments (${comments.length})`, icon: MessageSquare },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/scans" className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
          <ArrowLeft size={20} />
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold">{scan.title}</h1>
          <p className="text-sm text-gray-500 mt-1 flex items-center gap-2">
            <Globe size={14} /> {scan.target}
            <span className="text-gray-300 dark:text-gray-600">•</span>
            <Clock size={14} /> {new Date(scan.created_at).toLocaleString()}
          </p>
        </div>
        <a href={scanAPI.downloadPDF(scan.id)} target="_blank" rel="noreferrer" className="btn-secondary flex items-center gap-2">
          <Download size={16} /> Export PDF
        </a>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className={`card p-4 text-center ${getRiskBg(scan.risk_score)}`}>
          <div className={`text-3xl font-bold ${getRiskColor(scan.risk_score)}`}>{scan.risk_score}</div>
          <div className="text-xs font-medium uppercase mt-1 text-gray-500">Risk Score</div>
          <span className={`badge mt-2 ${getRiskBadge(getRiskLabel(scan.risk_score).toLowerCase())}`}>{getRiskLabel(scan.risk_score)}</span>
        </div>
        <div className="card p-4 text-center">
          <div className="text-3xl font-bold text-green-500">{scan.open_ports}</div>
          <div className="text-xs font-medium uppercase mt-1 text-gray-500">Open Ports</div>
        </div>
        <div className="card p-4 text-center">
          <div className="text-3xl font-bold text-gray-400">{scan.closed_ports}</div>
          <div className="text-xs font-medium uppercase mt-1 text-gray-500">Closed Ports</div>
        </div>
        <div className="card p-4 text-center">
          <div className="text-3xl font-bold text-orange-500">{scan.outdated_services?.length || 0}</div>
          <div className="text-xs font-medium uppercase mt-1 text-gray-500">Outdated</div>
        </div>
      </div>

      <div className="flex gap-1 border-b border-gray-200 dark:border-gray-800 overflow-x-auto">
        {tabs.map(({ id: tabId, label, icon: Icon }) => (
          <button key={tabId} onClick={() => setActiveTab(tabId)}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
              activeTab === tabId
                ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
            }`}>
            <Icon size={16} /> {label}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && (
        <div className="space-y-6 animate-in">
          {scan.ai_summary && (
            <div className="card p-6">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Brain size={18} className="text-primary-500" /> AI Analysis Summary
              </h3>
              <div className="bg-primary-500/5 dark:bg-primary-500/10 rounded-xl p-5 border border-primary-500/10">
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{scan.ai_summary}</p>
              </div>
            </div>
          )}

          {scan.outdated_services?.length > 0 && (
            <div className="card p-6">
              <h3 className="font-semibold mb-3 flex items-center gap-2 text-orange-500">
                <AlertTriangle size={18} /> Outdated Services
              </h3>
              <div className="space-y-2">
                {scan.outdated_services.map((svc, i) => (
                  <div key={i} className="flex items-center gap-3 bg-orange-500/5 dark:bg-orange-500/10 rounded-lg p-3 border border-orange-500/10">
                    <span className="font-mono text-sm font-medium text-orange-500">{svc.port}</span>
                    <span className="text-sm">{svc.product || svc.service}</span>
                    <span className="badge bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400 text-xs">{svc.version || 'unknown'}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="card p-6">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <FileText size={18} className="text-primary-500" /> Scan Details
            </h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              {[
                ['Scan Type', scan.scan_type.toUpperCase()],
                ['File Type', scan.file_type.toUpperCase()],
                ['Total Ports', scan.total_ports],
                ['Status', scan.status],
                ['Target', scan.target],
              ].map(([label, value]) => (
                <div key={label} className="flex justify-between py-2 border-b border-gray-100 dark:border-gray-800">
                  <span className="text-gray-500">{label}</span>
                  <span className="font-medium">{value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'ports' && (
        <div className="space-y-4 animate-in">
          <div className="flex gap-2 text-sm">
            <span className="badge bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">{openPorts.length} open</span>
            <span className="badge bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400">{closedPorts.length} closed</span>
            <span className="badge bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">{filteredPorts.length} filtered</span>
          </div>

          <div className="space-y-3">
            {openPorts.map(port => (
              <div key={port.id} className="card p-5">
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center font-mono text-sm font-bold flex-shrink-0 ${getRiskBg(getRiskScoreForLevel(port.risk_level))} ${getRiskColor(getRiskScoreForLevel(port.risk_level))}`}>
                    {port.port_number}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-mono font-semibold">{port.port_number}/{port.protocol}</span>
                      <span className={`badge ${getRiskBadge(port.risk_level)}`}>{port.risk_level}</span>
                      {port.is_outdated && <span className="badge bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400">OUTDATED</span>}
                    </div>
                    <div className="flex items-center gap-3 text-sm text-gray-500 mb-2">
                      <span className="font-medium text-gray-700 dark:text-gray-300">{port.service || 'Unknown'}</span>
                      {port.banner && <span className="font-mono text-xs bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">{port.banner}</span>}
                    </div>
                    {port.ai_explanation && (
                      <div className="bg-primary-500/5 dark:bg-primary-500/10 rounded-lg p-3 border border-primary-500/10 mt-2">
                        <div className="flex items-center gap-1.5 mb-1">
                          <Brain size={14} className="text-primary-500" />
                          <span className="text-xs font-medium text-primary-500">AI Explanation</span>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">{port.ai_explanation}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {closedPorts.length > 0 && (
            <details className="card">
              <summary className="p-4 cursor-pointer text-sm font-medium text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                Closed Ports ({closedPorts.length})
              </summary>
              <div className="px-4 pb-4 space-y-1">
                {closedPorts.map(port => (
                  <div key={port.id} className="flex items-center gap-3 py-1.5 text-sm text-gray-400">
                    <span className="font-mono">{port.port_number}/{port.protocol}</span>
                    <span>{port.service || ''}</span>
                  </div>
                ))}
              </div>
            </details>
          )}
        </div>
      )}

      {activeTab === 'recommendations' && (
        <div className="space-y-4 animate-in">
          {scan.ai_recommendations?.length > 0 ? scan.ai_recommendations.map((rec, i) => (
            <div key={i} className="card p-5 border-l-4" style={{ borderLeftColor: getBorderColor(rec.severity) }}>
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold">{rec.title}</h3>
                <span className={`badge ${getRiskBadge(rec.severity)}`}>{rec.severity}</span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{rec.description}</p>
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle size={14} className="text-green-500" />
                <span className="text-gray-500">Action:</span>
                <span className="font-medium">{rec.action}</span>
              </div>
              {rec.category && (
                <span className="inline-block mt-2 text-xs bg-gray-100 dark:bg-gray-800 text-gray-500 px-2 py-0.5 rounded">{rec.category}</span>
              )}
            </div>
          )) : (
            <div className="card p-8 text-center text-gray-400">
              <CheckCircle size={48} className="mx-auto mb-3 text-green-500/50" />
              <p>No specific recommendations. Your scan looks clean!</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'comments' && (
        <div className="space-y-4 animate-in">
          <div className="space-y-3">
            {comments.map(c => (
              <div key={c.id} className="card p-4">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-7 h-7 bg-primary-500/20 rounded-full flex items-center justify-center text-xs font-bold text-primary-600">
                    {c.user_name?.[0] || '?'}
                  </div>
                  <span className="text-sm font-medium">{c.user_name}</span>
                  <span className="text-xs text-gray-400">{new Date(c.created_at).toLocaleString()}</span>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">{c.content}</p>
              </div>
            ))}
            {comments.length === 0 && <p className="text-center text-gray-400 py-4">No comments yet.</p>}
          </div>

          <form onSubmit={addComment} className="flex gap-2">
            <input
              type="text" value={newComment} onChange={(e) => setNewComment(e.target.value)}
              className="input flex-1" placeholder="Add a comment..."
            />
            <button type="submit" className="btn-primary px-4" disabled={!newComment.trim()}>
              <Send size={16} />
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

function getRiskScoreForLevel(level) {
  return { critical: 90, high: 70, medium: 50, low: 10 }[level] || 10;
}

function getBorderColor(severity) {
  return { critical: '#dc2626', high: '#ea580c', medium: '#d97706', low: '#16a34a' }[severity] || '#16a34a';
}

function ScanDetailSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-8 bg-gray-200 dark:bg-gray-800 rounded w-64" />
      <div className="grid grid-cols-4 gap-4">
        {[1,2,3,4].map(i => <div key={i} className="card h-24 bg-gray-100 dark:bg-gray-800/50" />)}
      </div>
      <div className="card h-64 bg-gray-100 dark:bg-gray-800/50" />
    </div>
  );
}
