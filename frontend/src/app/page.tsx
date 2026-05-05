"use client";

import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { Session } from '@supabase/supabase-js';
import { User } from 'lucide-react';
import ChatBox from '@/components/ChatBox';
import MenuDashboard from '@/components/MenuDashboard';
import StoreManager from '@/components/StoreManager';

export default function Home() {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [session, setSession] = useState<Session | null>(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(true);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showDashboard, setShowDashboard] = useState(false);
  const [activePlatform, setActivePlatform] = useState<string | null>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setLoading(false);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const { error } = await supabase.auth.signUp({ email, password });
    if (error) alert(error.message);
    else alert('Check your email for the login link!');
    setLoading(false);
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) alert(error.message);
    setLoading(false);
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
  };

  if (loading) return <div style={{ height: '100vh', background: '#000' }} />;

  if (!session) {
    return (
      <div className="h-screen bg-black text-white flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-[320px]">
          <h1 className="text-2xl tracking-[0.1em] uppercase mb-8 font-light">
            MenuFlow
          </h1>
          <form className="flex flex-col gap-4">
            <input
              type="email"
              placeholder="EMAIL"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="bg-transparent border border-[#333] text-white px-4 py-3 text-xs tracking-[0.1em] focus:outline-none focus:border-[#666] transition-colors rounded-none w-full"
            />
            <input
              type="password"
              placeholder="PASSWORD"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="bg-transparent border border-[#333] text-white px-4 py-3 text-xs tracking-[0.1em] focus:outline-none focus:border-[#666] transition-colors rounded-none w-full"
            />
            <div className="flex gap-2 mt-2">
              <button onClick={handleLogin} disabled={loading} className="flex-1 bg-white text-black border-none p-3 text-[11px] uppercase tracking-[0.1em] cursor-pointer disabled:opacity-50">
                Login
              </button>
              <button onClick={handleSignUp} disabled={loading} className="flex-1 bg-transparent text-white border border-[#333] p-3 text-[11px] uppercase tracking-[0.1em] cursor-pointer disabled:opacity-50">
                Sign Up
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  const handleMenuUpdate = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 2000);
  };

  return (
    <div className="h-screen flex flex-col bg-black text-white overflow-hidden">
      {/* Top bar */}
      <header className="border-b border-[#1a1a1a] px-4 py-3 md:px-16 md:py-5 flex items-center justify-between shrink-0">
        <span className="text-sm md:text-lg tracking-[0.3em] uppercase text-white font-light">
          MenuFlow
        </span>
        <div className="relative">
          <button 
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            className="bg-transparent border border-[#333] rounded-full w-8 h-8 md:w-9 md:h-9 flex items-center justify-center cursor-pointer text-white hover:bg-[#111] transition-colors"
          >
            <User size={14} />
          </button>
          
          {showProfileMenu && (
            <div className="absolute top-10 right-0 w-40 bg-black border border-[#333] flex flex-col z-50">
              <button className="bg-transparent text-white border-none border-b border-[#1a1a1a] px-4 py-3 text-left text-[10px] tracking-[0.1em] uppercase cursor-pointer hover:bg-[#111]" onClick={() => { setShowProfileMenu(false); setShowDashboard(true); }}>Dashboard</button>
              <button className="bg-transparent text-white border-none border-b border-[#1a1a1a] px-4 py-3 text-left text-[10px] tracking-[0.1em] uppercase cursor-pointer hover:bg-[#111]" onClick={() => setShowProfileMenu(false)}>Settings</button>
              <button onClick={() => { setShowProfileMenu(false); handleLogout(); }} className="bg-transparent text-[#e74c3c] border-none px-4 py-3 text-left text-[10px] tracking-[0.1em] uppercase cursor-pointer hover:bg-[#111]">Logout</button>
            </div>
          )}
        </div>
      </header>

      {/* Main columns — stack on mobile, side-by-side on md+ */}
      <div className="flex flex-col md:flex-row flex-1 overflow-hidden">
        {/* Left — Chat */}
        <div className="flex-1 md:w-1/2 border-b md:border-b-0 md:border-r border-[#1a1a1a] flex flex-col overflow-hidden min-h-0">
          <div className="px-4 py-2 md:px-12 md:py-4 border-b border-[#1a1a1a] shrink-0 flex justify-center bg-[#050505]">
            <span className="text-[10px] md:text-[12px] tracking-[0.25em] uppercase text-[#ccc] font-medium">Chat</span>
          </div>
          <ChatBox onMenuUpdate={handleMenuUpdate} activePlatform={activePlatform} setActivePlatform={setActivePlatform} />
        </div>

        {/* Right — Dashboard */}
        <div className="flex-1 md:w-1/2 flex flex-col overflow-hidden min-h-0">
          <div className="px-4 py-2 md:px-12 md:py-4 border-b border-[#1a1a1a] shrink-0 flex justify-center bg-[#050505]">
            <span className="text-[10px] md:text-[12px] tracking-[0.25em] uppercase text-[#ccc] font-medium">Menu</span>
          </div>
          <MenuDashboard isRefreshing={isRefreshing} activePlatform={activePlatform} />
        </div>
      </div>

      {showDashboard && <StoreManager onClose={() => setShowDashboard(false)} />}
    </div>
  );
}
