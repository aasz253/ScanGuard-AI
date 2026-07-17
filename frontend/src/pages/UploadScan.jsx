import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { scanAPI } from '../utils/api';
import { Upload, FileText, X, Zap, Shield, Globe, Settings } from 'lucide-react';
import toast from 'react-hot-toast';

export default function UploadScan() {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [target, setTarget] = useState('');
  const [scanType, setScanType] = useState('full');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const navigate = useNavigate();

  const onDrop = useCallback((accepted) => {
    if (accepted.length > 0) {
      const f = accepted[0];
      setFile(f);
      if (!title) setTitle(f.name.replace(/\.[^/.]+$/, ''));
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/xml': ['.xml'],
      'application/xml': ['.xml'],
      'text/plain': ['.nmap', '.gnmap'],
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) { toast.error('Please select a file'); return; }
    if (!title.trim()) { toast.error('Please enter a title'); return; }
    if (!target.trim()) { toast.error('Please enter a target'); return; }

    setUploading(true);
    setProgress(10);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('target', target);
    formData.append('scan_type', scanType);

    try {
      setProgress(30);
      const res = await scanAPI.upload(formData);
      setProgress(80);

      toast.success('Scan uploaded! Processing with AI...');
      setProgress(100);

      setTimeout(() => navigate(`/scans/${res.data.id}`), 500);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed');
      setUploading(false);
      setProgress(0);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Upload Nmap Scan</h1>
        <p className="text-sm text-gray-500 mt-1">Upload your Nmap scan results for AI-powered analysis</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="card p-6">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <FileText size={18} className="text-primary-500" /> Scan File
          </h3>

          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all ${
              isDragActive
                ? 'border-primary-500 bg-primary-500/5'
                : file
                ? 'border-green-500 bg-green-500/5'
                : 'border-gray-300 dark:border-gray-700 hover:border-primary-400 dark:hover:border-primary-600'
            }`}
          >
            <input {...getInputProps()} />
            {file ? (
              <div className="space-y-2">
                <div className="w-14 h-14 bg-green-500/10 rounded-xl flex items-center justify-center mx-auto">
                  <FileText size={28} className="text-green-500" />
                </div>
                <p className="font-medium">{file.name}</p>
                <p className="text-sm text-gray-400">{(file.size / 1024).toFixed(1)} KB</p>
                <button type="button" onClick={(e) => { e.stopPropagation(); setFile(null); }} className="text-sm text-red-500 hover:text-red-600 flex items-center gap-1 mx-auto mt-2">
                  <X size={14} /> Remove
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="w-14 h-14 bg-gray-100 dark:bg-gray-800 rounded-xl flex items-center justify-center mx-auto">
                  <Upload size={28} className="text-gray-400" />
                </div>
                <p className="font-medium">{isDragActive ? 'Drop your file here' : 'Drag & drop your scan file'}</p>
                <p className="text-sm text-gray-400">Accepts .xml, .nmap, .gnmap (max 50MB)</p>
              </div>
            )}
          </div>
        </div>

        <div className="card p-6 space-y-5">
          <h3 className="font-semibold flex items-center gap-2">
            <Settings size={18} className="text-primary-500" /> Scan Details
          </h3>

          <div>
            <label className="block text-sm font-medium mb-1.5">Title</label>
            <input
              type="text" value={title} onChange={(e) => setTitle(e.target.value)}
              className="input" placeholder="e.g., Q4 Network Security Audit"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5 flex items-center gap-1.5">
              <Globe size={14} /> Target
            </label>
            <input
              type="text" value={target} onChange={(e) => setTarget(e.target.value)}
              className="input font-mono" placeholder="e.g., 192.168.1.0/24 or company.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5 flex items-center gap-1.5">
              <Zap size={14} /> Scan Type
            </label>
            <div className="grid grid-cols-4 gap-3">
              {[
                { value: 'quick', label: 'Quick', desc: 'Fast check' },
                { value: 'full', label: 'Full', desc: 'All ports' },
                { value: 'stealth', label: 'Stealth', desc: 'Low detection' },
                { value: 'custom', label: 'Custom', desc: 'Custom config' },
              ].map(({ value, label, desc }) => (
                <button
                  key={value} type="button" onClick={() => setScanType(value)}
                  className={`p-3 rounded-lg border-2 text-center transition-all ${
                    scanType === value
                      ? 'border-primary-500 bg-primary-500/5'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                >
                  <p className="text-sm font-medium">{label}</p>
                  <p className="text-[10px] text-gray-400 mt-0.5">{desc}</p>
                </button>
              ))}
            </div>
          </div>
        </div>

        {uploading && (
          <div className="card p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-primary-500 border-t-transparent" />
              <span className="text-sm font-medium">
                {progress < 50 ? 'Uploading...' : progress < 80 ? 'AI analyzing scan results...' : 'Finalizing...'}
              </span>
              <span className="text-sm text-gray-400 ml-auto">{progress}%</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div className="bg-primary-500 h-2 rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
            </div>
          </div>
        )}

        <button type="submit" disabled={uploading || !file} className="btn-primary w-full py-3 flex items-center justify-center gap-2 text-base disabled:opacity-50 disabled:cursor-not-allowed">
          {uploading ? (
            <><div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" /> Processing...</>
          ) : (
            <><Shield size={18} /> Analyze with AI</>
          )}
        </button>
      </form>
    </div>
  );
}
