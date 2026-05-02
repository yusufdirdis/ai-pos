"use client";

import { useState } from 'react';
import { X, Plus, Store, Settings, ChevronRight } from 'lucide-react';

export default function StoreManager({ onClose }: { onClose: () => void }) {
  const [stores, setStores] = useState([
    { id: 1, name: 'Downtown Square', pos: 'Square', platforms: ['UberEats', 'DoorDash'] }
  ]);
  const [isAdding, setIsAdding] = useState(false);
  const [newStore, setNewStore] = useState({ name: '', pos: '', platforms: [] as string[] });

  const POS_OPTIONS = ['Square', 'Clover', 'Lightspeed', 'Toast', 'Brink'];
  const PLATFORM_OPTIONS = ['UberEats', 'DoorDash', 'Grubhub', 'Postmates'];

  const togglePlatform = (p: string) => {
    setNewStore(prev => ({
      ...prev,
      platforms: prev.platforms.includes(p) ? prev.platforms.filter(x => x !== p) : [...prev.platforms, p]
    }));
  };

  const saveStore = () => {
    setStores([...stores, { id: Date.now(), ...newStore }]);
    setIsAdding(false);
    setNewStore({ name: '', pos: '', platforms: [] });
  };

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ width: '100%', maxWidth: 600, background: '#0a0a0a', border: '1px solid #222', display: 'flex', flexDirection: 'column', maxHeight: '80vh' }}>
        
        {/* Header */}
        <div style={{ padding: '24px 32px', borderBottom: '1px solid #222', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: 12, letterSpacing: '0.2em', textTransform: 'uppercase', color: '#fff' }}>Store Dashboard</span>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#555', cursor: 'pointer' }}><X size={16} /></button>
        </div>

        {/* Content */}
        <div style={{ flex: 1, overflowY: 'auto', padding: 32 }}>
          {!isAdding ? (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                <span style={{ fontSize: 10, color: '#666', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Connected POS Systems</span>
                <button 
                  onClick={() => setIsAdding(true)}
                  style={{ display: 'flex', alignItems: 'center', gap: 8, background: '#fff', color: '#000', border: 'none', padding: '8px 16px', fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.1em', cursor: 'pointer' }}
                >
                  <Plus size={12} /> Add POS System
                </button>
              </div>

              {stores.map(store => (
                <div key={store.id} style={{ border: '1px solid #222', padding: 20, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 20 }}>
                  <div style={{ width: 40, height: 40, background: '#111', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Store size={16} color="#555" />
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 14, color: '#fff', marginBottom: 4 }}>{store.name}</div>
                    <div style={{ fontSize: 10, color: '#666', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                      POS: <span style={{ color: '#ccc' }}>{store.pos}</span> &nbsp;&nbsp;&bull;&nbsp;&nbsp; Platforms: <span style={{ color: '#ccc' }}>{store.platforms.join(', ')}</span>
                    </div>
                  </div>
                  <button style={{ background: 'none', border: 'none', color: '#555', cursor: 'pointer' }}><Settings size={14} /></button>
                </div>
              ))}
            </>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
              <div>
                <label style={{ display: 'block', fontSize: 10, color: '#666', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 8 }}>Store Name</label>
                <input 
                  type="text" 
                  value={newStore.name} 
                  onChange={e => setNewStore({...newStore, name: e.target.value})}
                  placeholder="e.g. Uptown Location"
                  style={{ width: '100%', background: 'transparent', border: '1px solid #333', color: '#fff', padding: '12px 16px', fontSize: 12 }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: 10, color: '#666', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 8 }}>Select POS System</label>
                <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                  {POS_OPTIONS.map(pos => (
                    <button 
                      key={pos}
                      onClick={() => setNewStore({...newStore, pos})}
                      style={{ 
                        background: newStore.pos === pos ? '#fff' : 'transparent',
                        color: newStore.pos === pos ? '#000' : '#888',
                        border: '1px solid #333',
                        padding: '10px 16px', fontSize: 11, cursor: 'pointer', textTransform: 'uppercase', letterSpacing: '0.05em'
                      }}
                    >
                      {pos}
                    </button>
                  ))}
                </div>
              </div>

              {newStore.pos && (
                <div>
                  <label style={{ display: 'block', fontSize: 10, color: '#666', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 8 }}>Select Delivery Platforms to Sync</label>
                  <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                    {PLATFORM_OPTIONS.map(plat => (
                      <button 
                        key={plat}
                        onClick={() => togglePlatform(plat)}
                        style={{ 
                          background: newStore.platforms.includes(plat) ? '#222' : 'transparent',
                          color: newStore.platforms.includes(plat) ? '#fff' : '#888',
                          border: newStore.platforms.includes(plat) ? '1px solid #555' : '1px solid #333',
                          padding: '10px 16px', fontSize: 11, cursor: 'pointer', textTransform: 'uppercase', letterSpacing: '0.05em'
                        }}
                      >
                        {plat}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
                <button 
                  onClick={saveStore}
                  disabled={!newStore.name || !newStore.pos}
                  style={{ flex: 1, background: '#fff', color: '#000', border: 'none', padding: 14, fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.1em', cursor: 'pointer', opacity: (!newStore.name || !newStore.pos) ? 0.5 : 1 }}
                >
                  Connect & Sync Menu
                </button>
                <button 
                  onClick={() => setIsAdding(false)}
                  style={{ background: 'transparent', color: '#888', border: '1px solid #333', padding: '14px 24px', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.1em', cursor: 'pointer' }}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
