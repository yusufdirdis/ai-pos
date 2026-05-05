"use client";

import { useState, useEffect } from 'react';
import { RefreshCw, Download } from 'lucide-react';

export default function MenuDashboard({ isRefreshing, activePlatform }: { isRefreshing: boolean, activePlatform: string | null }) {
  const [items, setItems] = useState<any[]>([]);
  const [isPulling, setIsPulling] = useState(false);
  const [pullResult, setPullResult] = useState<string | null>(null);

  useEffect(() => { fetchItems(); }, [isRefreshing, activePlatform]);

  const fetchItems = async () => {
    try {
      const url = activePlatform 
        ? `http://localhost:8000/api/items/menu?platform=${activePlatform}` 
        : `http://localhost:8000/api/items/menu`;
      const res = await fetch(url);
      const data = await res.json();
      setItems(data);
    } catch (e) { console.error(e); }
  };

  const pullMenu = async () => {
    setIsPulling(true);
    setPullResult(null);
    try {
      const formData = new FormData();
      formData.append('platform', 'ubereats');
      const res = await fetch('http://localhost:8000/api/items/pull-menu', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setPullResult(`Imported ${data.imported} new, updated ${data.updated} existing`);
      fetchItems(); // Refresh the list
    } catch (e) {
      setPullResult('Failed to pull menu');
      console.error(e);
    }
    setIsPulling(false);
    setTimeout(() => setPullResult(null), 4000);
  };

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Toolbar row */}
      <div className="px-4 py-3 md:px-12 md:py-4 border-b border-[#1a1a1a] flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <button 
            onClick={pullMenu} 
            disabled={isPulling}
            className="flex items-center gap-1.5 text-[9px] md:text-[10px] tracking-[0.1em] uppercase px-3 py-1.5 border border-[#333] bg-transparent text-[#888] cursor-pointer hover:text-white hover:border-[#555] transition-colors disabled:opacity-50"
          >
            <Download size={10} className={isPulling ? 'animate-bounce' : ''} />
            {isPulling ? 'Pulling...' : 'Pull Menu'}
          </button>
          {pullResult && (
            <span className="text-[9px] text-[#2ecc71] tracking-[0.05em]">{pullResult}</span>
          )}
        </div>
        <button onClick={fetchItems} className="bg-transparent border-none cursor-pointer text-[#444] flex items-center p-0 hover:text-white transition-colors">
          <RefreshCw size={12} className={isRefreshing ? 'animate-spin' : ''} />
        </button>
      </div>


      {/* Item list */}
      <div className="flex-1 overflow-y-auto relative">
        {items.length === 0 && !isRefreshing && (
          <div className="p-8 md:p-16 text-xs text-[#333] tracking-[0.05em] text-center">
            No items. Ask the AI to add something.
          </div>
        )}

        {items.map((item, i) => (
          <div key={item.id} className="px-4 py-4 md:px-12 md:py-5 border-b border-[#1a1a1a] flex items-center gap-4 md:gap-5 transition-colors hover:bg-[#0a0a0a]">
            {/* Image or index */}
            {item.image ? (
              <img src={item.image} alt={item.name} className="w-10 h-10 md:w-11 md:h-11 object-cover shrink-0 rounded-none" />
            ) : (
              <div className="w-10 h-10 md:w-11 md:h-11 bg-[#111] shrink-0 flex items-center justify-center text-[11px] text-[#333] font-medium rounded-none">
                {String(i + 1).padStart(2, '0')}
              </div>
            )}

            {/* Name + price */}
            <div className="flex-1 min-w-0">
              <div className="text-[12px] md:text-[13px] text-white tracking-[0.01em] mb-1 truncate">
                {item.name}
              </div>
              <div className="text-[10px] md:text-[11px] text-[#555] tracking-[0.05em]">
                {item.price}
              </div>
            </div>

            {/* Platforms + status */}
            <div className="flex flex-col items-end gap-1.5 shrink-0">
              <div className="flex gap-1.5 flex-wrap justify-end max-w-[80px] md:max-w-none">
                {item.platforms?.map((p: string) => (
                  <span key={p} className="text-[8px] md:text-[9px] tracking-[0.12em] uppercase text-[#555] border border-[#222] px-1.5 py-0.5 whitespace-nowrap">
                    {p}
                  </span>
                ))}
              </div>
              <span className={`text-[8px] md:text-[9px] tracking-[0.12em] uppercase ${item.status === 'Synced' ? 'text-[#2ecc71]' : item.status === 'Failed' ? 'text-[#e74c3c]' : 'text-[#f39c12]'}`}>
                {item.status}
              </span>
            </div>
          </div>
        ))}

        {isRefreshing && (
          <div className="p-4 md:p-5 text-[10px] md:text-[11px] text-[#444] tracking-[0.1em] uppercase text-center absolute bottom-0 left-0 right-0 bg-black/80 backdrop-blur-sm border-t border-[#1a1a1a]">
            Syncing...
          </div>
        )}
      </div>
    </div>
  );
}
