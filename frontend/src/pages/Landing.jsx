import { Link } from 'react-router-dom';
import { Shield, Upload, Brain, FileText, BarChart3, Users, ChevronRight, Zap, Lock, Eye } from 'lucide-react';

export default function Landing() {
  const features = [
    { icon: Upload, title: 'Upload Nmap Scans', desc: 'Drop your .xml, .nmap, or .gnmap files and get instant analysis.' },
    { icon: Brain, title: 'AI-Powered Analysis', desc: 'OpenRouter GPT explains every port finding in plain English.' },
    { icon: Shield, title: 'Risk Scoring', desc: '0-100 risk score based on ports, services, and vulnerabilities.' },
    { icon: Zap, title: 'Outdated Detection', desc: 'Automatically flag outdated services with known CVEs.' },
    { icon: FileText, title: 'PDF Reports', desc: 'Generate professional security reports for stakeholders.' },
    { icon: BarChart3, title: 'Dashboard & Charts', desc: 'Visual overview of your security posture with trend tracking.' },
    { icon: Eye, title: 'Compare Scans', desc: 'Track improvements over time with scan history comparison.' },
    { icon: Users, title: 'Team Management', desc: 'Collaborate with your team on security assessments.' },
    { icon: Lock, title: 'Dark Mode', desc: 'Built-in dark mode for late-night security reviews.' },
  ];

  return (
    <div className="min-h-screen bg-navy-950 text-white">
      <nav className="flex items-center justify-between px-8 py-5 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center shadow-lg shadow-primary-500/20">
            <Shield size={22} className="text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-wide">ScanGuard AI</h1>
            <span className="text-[10px] text-primary-400 font-medium tracking-[0.2em] uppercase">Network Security Platform</span>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <Link to="/login" className="text-sm text-gray-400 hover:text-white transition-colors">Sign In</Link>
          <Link to="/register" className="btn-primary text-sm">Get Started Free</Link>
        </div>
      </nav>

      <section className="max-w-6xl mx-auto px-8 pt-24 pb-32 text-center">
        <div className="inline-flex items-center gap-2 bg-primary-500/10 border border-primary-500/20 rounded-full px-4 py-1.5 mb-8">
          <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          <span className="text-xs text-primary-300 font-medium">AI-Powered Network Security Analysis</span>
        </div>

        <h1 className="text-5xl md:text-7xl font-extrabold leading-tight mb-6">
          Know What's{' '}
          <span className="bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
            Exposed
          </span>
          <br />On Your Network
        </h1>

        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          Upload Nmap scan results and let AI explain every open port, identify risks,
          and give you actionable security recommendations — in plain English.
        </p>

        <div className="flex items-center justify-center gap-4">
          <Link to="/register" className="btn-primary text-base px-8 py-3 flex items-center gap-2">
            Start Scanning <ChevronRight size={18} />
          </Link>
          <a href="#features" className="btn-secondary text-base px-8 py-3">
            Learn More
          </a>
        </div>

        <div className="mt-16 relative">
          <div className="absolute inset-0 bg-gradient-to-b from-primary-500/10 to-transparent rounded-3xl blur-3xl" />
          <div className="relative bg-gray-900/80 border border-gray-800 rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-3 h-3 rounded-full bg-red-500/80" />
              <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
              <div className="w-3 h-3 rounded-full bg-green-500/80" />
              <span className="text-xs text-gray-500 ml-4 font-mono">scanguard-dashboard</span>
            </div>
            <div className="grid grid-cols-4 gap-4 mb-4">
              {[
                { label: 'Risk Score', value: '42', color: 'text-yellow-400' },
                { label: 'Open Ports', value: '8', color: 'text-green-400' },
                { label: 'High Risk', value: '2', color: 'text-red-400' },
                { label: 'Outdated', value: '3', color: 'text-orange-400' },
              ].map(({ label, value, color }) => (
                <div key={label} className="bg-gray-800/50 rounded-lg p-3 text-center">
                  <div className={`text-2xl font-bold ${color}`}>{value}</div>
                  <div className="text-xs text-gray-500 mt-1">{label}</div>
                </div>
              ))}
            </div>
            <div className="space-y-2">
              {[
                { port: '22/tcp', service: 'OpenSSH 8.9', risk: 'low', desc: 'Secure remote access — keep updated' },
                { port: '80/tcp', service: 'nginx 1.22', risk: 'low', desc: 'Web server — ensure HTTPS enabled' },
                { port: '445/tcp', service: 'Samba 4.15', risk: 'high', desc: 'File sharing — restrict access immediately' },
                { port: '3389/tcp', service: 'RDP', risk: 'critical', desc: 'Remote desktop — use VPN instead' },
              ].map(({ port, service, risk, desc }) => (
                <div key={port} className="flex items-center gap-4 bg-gray-800/30 rounded-lg px-4 py-2.5 text-sm">
                  <span className="font-mono text-primary-400 w-20">{port}</span>
                  <span className="text-gray-300 w-32">{service}</span>
                  <span className={`badge ${risk === 'critical' ? 'bg-red-500/20 text-red-400' : risk === 'high' ? 'bg-orange-500/20 text-orange-400' : 'bg-green-500/20 text-green-400'}`}>{risk}</span>
                  <span className="text-gray-500 flex-1">{desc}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="max-w-6xl mx-auto px-8 py-24 border-t border-white/5">
        <h2 className="text-3xl font-bold text-center mb-4">Everything You Need</h2>
        <p className="text-gray-400 text-center mb-16 max-w-xl mx-auto">Complete network security analysis platform built for SMEs and organizations.</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="card bg-gray-900/50 border-gray-800 p-6 hover:border-primary-500/30 transition-all group">
              <div className="w-10 h-10 bg-primary-500/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-primary-500/20 transition-colors">
                <Icon size={20} className="text-primary-400" />
              </div>
              <h3 className="font-semibold mb-2">{title}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-8 py-24 border-t border-white/5 text-center">
        <h2 className="text-3xl font-bold mb-4">Ready to Secure Your Network?</h2>
        <p className="text-gray-400 mb-8">Start scanning in under 60 seconds. No credit card required.</p>
        <Link to="/register" className="btn-primary text-base px-10 py-3 inline-flex items-center gap-2">
          Get Started Free <ChevronRight size={18} />
        </Link>
      </section>

      <footer className="border-t border-white/5 py-8 text-center text-sm text-gray-600">
        <p>ScanGuard AI — Nmap Scan Analysis Platform</p>
      </footer>
    </div>
  );
}
