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
    <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
      <div className="w-full max-w-[600px] bg-[#0a0a0a] border border-[#222] flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="px-6 py-5 border-b border-[#222] flex justify-between items-center shrink-0">
          <span className="text-[12px] tracking-[0.2em] uppercase text-white font-medium">Store Dashboard</span>
          <button onClick={onClose} className="bg-transparent border-none text-[#555] cursor-pointer p-1 hover:text-white transition-colors"><X size={16} /></button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 md:p-8">
          {!isAdding ? (
            <>
              <div className="flex justify-between items-center mb-6">
                <span className="text-[10px] text-[#666] uppercase tracking-[0.1em]">Connected POS Systems</span>
                <button 
                  onClick={() => setIsAdding(true)}
                  className="flex items-center gap-2 bg-white text-black border-none px-4 py-2 text-[10px] uppercase tracking-[0.1em] cursor-pointer hover:bg-gray-200 transition-colors"
                >
                  <Plus size={12} /> Add POS System
                </button>
              </div>

              {stores.map(store => (
                <div key={store.id} className="border border-[#222] p-5 mb-4 flex items-center gap-4 md:gap-5">
                  <div className="w-10 h-10 bg-[#111] flex items-center justify-center shrink-0">
                    <Store size={16} color="#555" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-[13px] md:text-[14px] text-white mb-1 truncate">{store.name}</div>
                    <div className="text-[9px] md:text-[10px] text-[#666] tracking-[0.05em] uppercase truncate">
                      POS: <span className="text-[#ccc]">{store.pos}</span> <span className="mx-2">&bull;</span> Platforms: <span className="text-[#ccc]">{store.platforms.join(', ')}</span>
                    </div>
                  </div>
                  <button className="bg-transparent border-none text-[#555] cursor-pointer p-1 shrink-0 hover:text-white transition-colors"><Settings size={14} /></button>
                </div>
              ))}
            </>
          ) : (
            <div className="flex flex-col gap-6">
              <div>
                <label className="block text-[10px] text-[#666] uppercase tracking-[0.1em] mb-2">Store Name</label>
                <input 
                  type="text" 
                  value={newStore.name} 
                  onChange={e => setNewStore({...newStore, name: e.target.value})}
                  placeholder="e.g. Uptown Location"
                  className="w-full bg-transparent border border-[#333] text-white px-4 py-3 text-[12px] focus:outline-none focus:border-[#666] rounded-none"
                />
              </div>

              <div>
                <label className="block text-[10px] text-[#666] uppercase tracking-[0.1em] mb-2">Select POS System</label>
                <div className="flex gap-3 flex-wrap">
                  {POS_OPTIONS.map(pos => (
                    <button 
                      key={pos}
                      onClick={() => setNewStore({...newStore, pos})}
                      className={`border border-[#333] px-4 py-2.5 text-[10px] md:text-[11px] cursor-pointer uppercase tracking-[0.05em] transition-colors rounded-none ${newStore.pos === pos ? 'bg-white text-black' : 'bg-transparent text-[#888]'}`}
                    >
                      {pos}
                    </button>
                  ))}
                </div>
              </div>

              {newStore.pos && (
                <div>
                  <label className="block text-[10px] text-[#666] uppercase tracking-[0.1em] mb-2">Select Delivery Platforms to Sync</label>
                  <div className="flex gap-3 flex-wrap">
                    {PLATFORM_OPTIONS.map(plat => (
                      <button 
                        key={plat}
                        onClick={() => togglePlatform(plat)}
                        className={`px-4 py-2.5 text-[10px] md:text-[11px] cursor-pointer uppercase tracking-[0.05em] transition-colors rounded-none ${newStore.platforms.includes(plat) ? 'bg-[#222] text-white border border-[#555]' : 'bg-transparent text-[#888] border border-[#333]'}`}
                      >
                        {plat}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex flex-col md:flex-row gap-3 mt-4">
                <button 
                  onClick={saveStore}
                  disabled={!newStore.name || !newStore.pos}
                  className={`flex-1 bg-white text-black border-none p-3.5 text-[11px] uppercase tracking-[0.1em] cursor-pointer rounded-none ${(!newStore.name || !newStore.pos) ? 'opacity-50' : 'hover:bg-gray-200'}`}
                >
                  Connect & Sync Menu
                </button>
                <button 
                  onClick={() => setIsAdding(false)}
                  className="bg-transparent text-[#888] border border-[#333] px-6 py-3.5 text-[11px] uppercase tracking-[0.1em] cursor-pointer rounded-none hover:text-white hover:border-[#555]"
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
