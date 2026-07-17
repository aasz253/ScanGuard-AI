import { useState, useEffect } from 'react';
import { teamAPI } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import { Users, Plus, Link2, Copy, LogOut, UserPlus, Shield } from 'lucide-react';
import toast from 'react-hot-toast';

export default function Team() {
  const { user } = useAuth();
  const [team, setTeam] = useState(null);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createMode, setCreateMode] = useState(false);
  const [joinMode, setJoinMode] = useState(false);
  const [teamName, setTeamName] = useState('');
  const [teamDesc, setTeamDesc] = useState('');
  const [inviteCode, setInviteCode] = useState('');

  useEffect(() => { loadTeam(); }, []);

  const loadTeam = async () => {
    try {
      const teamRes = await teamAPI.getMine();
      setTeam(teamRes.data);
      const membersRes = await teamAPI.members();
      setMembers(membersRes.data);
    } catch {
      setTeam(null);
    } finally {
      setLoading(false);
    }
  };

  const createTeam = async (e) => {
    e.preventDefault();
    if (!teamName.trim()) return;
    try {
      const res = await teamAPI.create({ name: teamName, description: teamDesc });
      setTeam(res.data);
      setCreateMode(false);
      toast.success('Team created! Share the invite code with your team.');
      loadTeam();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create team');
    }
  };

  const joinTeam = async (e) => {
    e.preventDefault();
    if (!inviteCode.trim()) return;
    try {
      const res = await teamAPI.join({ invite_code: inviteCode });
      setTeam(res.data);
      setJoinMode(false);
      toast.success('Joined team!');
      loadTeam();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Invalid invite code');
    }
  };

  const leaveTeam = async () => {
    if (!confirm('Leave this team?')) return;
    try {
      await teamAPI.leave();
      setTeam(null);
      setMembers([]);
      toast.success('Left team');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to leave team');
    }
  };

  const copyInviteCode = () => {
    if (team?.invite_code) {
      navigator.clipboard.writeText(team.invite_code);
      toast.success('Invite code copied!');
    }
  };

  if (loading) return <div className="space-y-4 animate-pulse"><div className="card h-40 bg-gray-100 dark:bg-gray-800/50" /></div>;

  if (!team && !createMode && !joinMode) {
    return (
      <div className="max-w-lg mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Team Management</h1>
          <p className="text-sm text-gray-500 mt-1">Collaborate on security scans with your team</p>
        </div>

        <div className="card p-8 text-center">
          <Users size={48} className="mx-auto text-gray-300 dark:text-gray-600 mb-4" />
          <h2 className="text-lg font-semibold mb-2">No Team Yet</h2>
          <p className="text-sm text-gray-500 mb-6">Create a new team or join an existing one to collaborate on scans.</p>

          <div className="space-y-3">
            <button onClick={() => setCreateMode(true)} className="btn-primary w-full flex items-center justify-center gap-2">
              <Plus size={16} /> Create Team
            </button>
            <button onClick={() => setJoinMode(true)} className="btn-secondary w-full flex items-center justify-center gap-2">
              <UserPlus size={16} /> Join with Invite Code
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (createMode) {
    return (
      <div className="max-w-lg mx-auto space-y-6">
        <h1 className="text-2xl font-bold">Create Team</h1>
        <form onSubmit={createTeam} className="card p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">Team Name</label>
            <input type="text" value={teamName} onChange={(e) => setTeamName(e.target.value)} className="input" placeholder="Security Team" required />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Description (optional)</label>
            <input type="text" value={teamDesc} onChange={(e) => setTeamDesc(e.target.value)} className="input" placeholder="Our network security team" />
          </div>
          <div className="flex gap-3">
            <button type="submit" className="btn-primary flex-1">Create</button>
            <button type="button" onClick={() => setCreateMode(false)} className="btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    );
  }

  if (joinMode) {
    return (
      <div className="max-w-lg mx-auto space-y-6">
        <h1 className="text-2xl font-bold">Join Team</h1>
        <form onSubmit={joinTeam} className="card p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">Invite Code</label>
            <input type="text" value={inviteCode} onChange={(e) => setInviteCode(e.target.value)} className="input font-mono" placeholder="Paste invite code here" required />
          </div>
          <div className="flex gap-3">
            <button type="submit" className="btn-primary flex-1">Join</button>
            <button type="button" onClick={() => setJoinMode(false)} className="btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{team.name}</h1>
          {team.description && <p className="text-sm text-gray-500 mt-1">{team.description}</p>}
        </div>
        <button onClick={leaveTeam} className="btn-secondary flex items-center gap-2 text-red-500 hover:text-red-600">
          <LogOut size={16} /> Leave Team
        </button>
      </div>

      <div className="card p-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-500/10 rounded-lg flex items-center justify-center">
            <Link2 size={18} className="text-primary-500" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium">Team Invite Code</p>
            <p className="font-mono text-sm text-gray-500">{team.invite_code}</p>
          </div>
          <button onClick={copyInviteCode} className="btn-secondary flex items-center gap-2 text-sm">
            <Copy size={14} /> Copy
          </button>
        </div>
      </div>

      <div className="card">
        <div className="p-5 border-b border-gray-200 dark:border-gray-800">
          <h3 className="font-semibold flex items-center gap-2">
            <Users size={18} className="text-primary-500" /> Members ({members.length})
          </h3>
        </div>
        <div className="divide-y divide-gray-100 dark:divide-gray-800">
          {members.map(m => (
            <div key={m.id} className="flex items-center gap-3 p-4">
              <div className="w-9 h-9 bg-gradient-to-br from-primary-500 to-primary-700 rounded-full flex items-center justify-center text-sm font-bold text-white">
                {m.full_name?.[0] || '?'}
              </div>
              <div className="flex-1">
                <p className="font-medium text-sm">{m.full_name}</p>
                <p className="text-xs text-gray-400">{m.email}</p>
              </div>
              <span className={`badge ${m.role === 'admin' ? 'bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400' : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'}`}>
                <Shield size={12} className="mr-1" />
                {m.role}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
