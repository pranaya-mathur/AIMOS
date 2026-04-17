"use client";

import { useEffect, useState } from "react";
import { getTeam, inviteMember, removeMember, type TeamListing } from "@/lib/api/team";

export default function TeamManagementPage() {
  const [data, setData] = useState<TeamListing | null>(null);
  const [loading, setLoading] = useState(true);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviting, setInviting] = useState(false);

  const fetchTeam = async () => {
    try {
      const listing = await getTeam();
      setData(listing);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTeam();
  }, []);

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    setInviting(true);
    try {
      await inviteMember(inviteEmail);
      setInviteEmail("");
      await fetchTeam();
      alert("Invite sent successfully!");
    } catch (e: any) {
      alert(e.message);
    } finally {
      setInviting(false);
    }
  };

  const handleRemove = async (userId: string) => {
    if (!confirm("Are you sure you want to remove this member?")) return;
    try {
      await removeMember(userId);
      await fetchTeam();
    } catch (e: any) {
      alert(e.message);
    }
  };

  if (loading) return <div className="p-20 text-center text-slate-400 font-medium">Synchronizing team data...</div>;

  return (
    <div className="max-w-4xl mx-auto p-10">
      <header className="mb-12">
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Team Management</h1>
        <p className="text-slate-500 mt-2 font-medium">Manage organization seats and delegate workspace authorities.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
        {/* Members List */}
        <div className="lg:col-span-2 space-y-8">
            <section>
                <h2 className="text-sm font-black uppercase tracking-widest text-slate-400 mb-6">Active Members</h2>
                <div className="space-y-4">
                    {data?.members.map((m) => (
                        <div key={m.id} className="flex items-center justify-between p-6 bg-white border border-slate-100 rounded-3xl shadow-sm">
                            <div>
                                <p className="font-bold text-slate-900">{m.email}</p>
                                <p className="text-[10px] uppercase font-black tracking-widest text-violet-500 mt-1">{m.role}</p>
                            </div>
                            <button 
                                onClick={() => handleRemove(m.id)}
                                className="text-[10px] font-black uppercase tracking-widest text-red-400 hover:text-red-600"
                            >
                                Remove
                            </button>
                        </div>
                    ))}
                </div>
            </section>

            {data?.pending_invites.length! > 0 && (
                <section>
                    <h2 className="text-sm font-black uppercase tracking-widest text-slate-400 mb-6">Pending Invites</h2>
                    <div className="space-y-4">
                        {data?.pending_invites.map((i) => (
                            <div key={i.id} className="flex items-center justify-between p-6 bg-slate-50 border border-dashed border-slate-200 rounded-3xl">
                                <div>
                                    <p className="font-bold text-slate-400">{i.email}</p>
                                    <p className="text-[10px] uppercase font-black tracking-widest text-slate-300 mt-1 italic">Expires {new Date(i.expires_at).toLocaleDateString()}</p>
                                </div>
                                <span className="text-[10px] font-black uppercase tracking-widest text-slate-300">Invite Sent</span>
                            </div>
                        ))}
                    </div>
                </section>
            )}
        </div>

        {/* Invite Form */}
        <div className="bg-slate-900 p-8 rounded-[2.5rem] shadow-2xl h-fit sticky top-8">
            <h3 className="text-lg font-bold text-white mb-6">Invite Member</h3>
            <form onSubmit={handleInvite} className="space-y-4">
                <div className="space-y-2">
                    <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Email Address</label>
                    <input 
                        type="email" 
                        required
                        value={inviteEmail}
                        onChange={(e) => setInviteEmail(e.target.value)}
                        placeholder="teammate@agency.com"
                        className="w-full bg-slate-800 border-none rounded-2xl p-4 text-white text-sm font-medium placeholder:text-slate-600 focus:ring-2 focus:ring-violet-500"
                    />
                </div>
                <button 
                    disabled={inviting}
                    className="w-full py-4 rounded-2xl bg-gradient-to-br from-violet-600 to-indigo-600 text-[10px] font-black uppercase tracking-widest text-white shadow-xl hover:scale-[1.02] transition-transform disabled:opacity-50"
                >
                    {inviting ? "Inviting..." : "Send Invitation"}
                </button>
            </form>
            <p className="text-[10px] text-slate-500 mt-6 leading-relaxed">
                Invited members will share your organization's campaign and token quotas.
            </p>
        </div>
      </div>
    </div>
  );
}
