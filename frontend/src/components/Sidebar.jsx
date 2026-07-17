import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Upload, ScanSearch, Users, Shield, X, ChevronLeft } from 'lucide-react';
import { useState } from 'react';

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/scans/upload', icon: Upload, label: 'Upload Scan' },
  { to: '/scans', icon: ScanSearch, label: 'Scan History' },
  { to: '/team', icon: Users, label: 'Team' },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside className={`${collapsed ? 'w-20' : 'w-64'} bg-navy-900 dark:bg-navy-950 text-white flex flex-col transition-all duration-300 border-r border-gray-800`}>
      <div className={`flex items-center ${collapsed ? 'justify-center' : 'justify-between'} px-5 h-16 border-b border-gray-800`}>
        {!collapsed && (
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center shadow-lg shadow-primary-500/20">
              <Shield size={20} className="text-white" />
            </div>
            <div>
              <h1 className="font-bold text-sm tracking-wide">ScanGuard</h1>
              <span className="text-[10px] text-primary-400 font-medium tracking-widest uppercase">AI</span>
            </div>
          </div>
        )}
        {collapsed && (
          <div className="w-9 h-9 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
            <Shield size={20} className="text-white" />
          </div>
        )}
        <button onClick={() => setCollapsed(!collapsed)} className={`text-gray-400 hover:text-white transition-colors ${collapsed ? 'hidden' : ''}`}>
          <ChevronLeft size={18} className={`transition-transform ${collapsed ? 'rotate-180' : ''}`} />
        </button>
      </div>

      <nav className="flex-1 py-4 space-y-1 px-3">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-primary-600/20 text-primary-400 shadow-sm'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              } ${collapsed ? 'justify-center' : ''}`
            }
            title={collapsed ? label : undefined}
          >
            <Icon size={20} />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      <div className={`p-4 border-t border-gray-800 ${collapsed ? 'hidden' : ''}`}>
        <div className="bg-gradient-to-r from-primary-600/10 to-primary-700/10 rounded-lg p-3 border border-primary-500/20">
          <p className="text-xs text-primary-300 font-medium">AI-Powered Analysis</p>
          <p className="text-[10px] text-gray-500 mt-1">OpenRouter GPT Integration</p>
        </div>
      </div>
    </aside>
  );
}
