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
      <div style={{
        height: '100vh',
        background: '#000',
        color: '#fff',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column'
      }}>
        <div style={{ width: '100%', maxWidth: 320 }}>
          <h1 style={{ fontSize: 24, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 32, fontWeight: 300 }}>
            MenuFlow
          </h1>
          <form style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <input
              type="email"
              placeholder="EMAIL"
              value={email}
              onChange={e => setEmail(e.target.value)}
              style={{ background: 'transparent', border: '1px solid #333', color: '#fff', padding: '12px 16px', fontSize: 12, letterSpacing: '0.1em' }}
            />
            <input
              type="password"
              placeholder="PASSWORD"
              value={password}
              onChange={e => setPassword(e.target.value)}
              style={{ background: 'transparent', border: '1px solid #333', color: '#fff', padding: '12px 16px', fontSize: 12, letterSpacing: '0.1em' }}
            />
            <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
              <button onClick={handleLogin} disabled={loading} style={{ flex: 1, background: '#fff', color: '#000', border: 'none', padding: '12px', fontSize: 11, cursor: 'pointer', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                Login
              </button>
              <button onClick={handleSignUp} disabled={loading} style={{ flex: 1, background: 'transparent', color: '#fff', border: '1px solid #333', padding: '12px', fontSize: 11, cursor: 'pointer', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
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
    <div style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: '#000',
      color: '#fff',
      overflow: 'hidden',
    }}>
      {/* Top bar */}
      <header style={{
        borderBottom: '1px solid #1a1a1a',
        padding: '14px 48px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexShrink: 0,
      }}>
        <span style={{ fontSize: 16, letterSpacing: '0.25em', textTransform: 'uppercase', color: '#fff', fontWeight: 400 }}>
          MenuFlow
        </span>
        <div style={{ position: 'relative' }}>
          <button 
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            style={{ 
              background: 'none', border: '1px solid #333', borderRadius: '50%', width: 32, height: 32, 
              display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: '#fff' 
            }}
          >
            <User size={14} />
          </button>
          
          {showProfileMenu && (
            <div style={{ 
              position: 'absolute', top: 40, right: 0, width: 160, 
              background: '#000', border: '1px solid #333', 
              display: 'flex', flexDirection: 'column', zIndex: 50 
            }}>
              <button style={{ background: 'transparent', color: '#fff', border: 'none', borderBottom: '1px solid #1a1a1a', padding: '12px 16px', textAlign: 'left', fontSize: 10, letterSpacing: '0.1em', textTransform: 'uppercase', cursor: 'pointer' }} onClick={() => { setShowProfileMenu(false); setShowDashboard(true); }}>Dashboard</button>
              <button style={{ background: 'transparent', color: '#fff', border: 'none', borderBottom: '1px solid #1a1a1a', padding: '12px 16px', textAlign: 'left', fontSize: 10, letterSpacing: '0.1em', textTransform: 'uppercase', cursor: 'pointer' }} onClick={() => setShowProfileMenu(false)}>Settings</button>
              <button onClick={() => { setShowProfileMenu(false); handleLogout(); }} style={{ background: 'transparent', color: '#e74c3c', border: 'none', padding: '12px 16px', textAlign: 'left', fontSize: 10, letterSpacing: '0.1em', textTransform: 'uppercase', cursor: 'pointer' }}>Logout</button>
            </div>
          )}
        </div>
      </header>

      {/* Main columns — fill remaining height */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', flex: 1, overflow: 'hidden' }}>
        {/* Left — Chat */}
        <div style={{ borderRight: '1px solid #1a1a1a', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ padding: '12px 48px', borderBottom: '1px solid #1a1a1a', flexShrink: 0, display: 'flex', justifyContent: 'center' }}>
            <span style={{ fontSize: 11, letterSpacing: '0.2em', textTransform: 'uppercase', color: '#ccc', fontWeight: 500 }}>Chat</span>
          </div>
          <ChatBox onMenuUpdate={handleMenuUpdate} activePlatform={activePlatform} setActivePlatform={setActivePlatform} />
        </div>

        {/* Right — Dashboard */}
        <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ padding: '12px 48px', borderBottom: '1px solid #1a1a1a', flexShrink: 0, display: 'flex', justifyContent: 'center' }}>
            <span style={{ fontSize: 11, letterSpacing: '0.2em', textTransform: 'uppercase', color: '#ccc', fontWeight: 500 }}>Menu</span>
          </div>
          <MenuDashboard isRefreshing={isRefreshing} activePlatform={activePlatform} />
        </div>
      </div>

      {showDashboard && <StoreManager onClose={() => setShowDashboard(false)} />}
    </div>
  );
}
