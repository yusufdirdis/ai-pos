"use client";

import { useState, useEffect } from 'react';
import { RefreshCw } from 'lucide-react';

export default function MenuDashboard({ isRefreshing, activePlatform }: { isRefreshing: boolean, activePlatform: string | null }) {
  const [items, setItems] = useState<any[]>([]);

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

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Item list */}
      <div style={{ flex: 1, overflowY: 'auto' }}>
        {items.length === 0 && !isRefreshing && (
          <div style={{ padding: '64px 48px', fontSize: 12, color: '#333', letterSpacing: '0.05em' }}>
            No items. Ask the AI to add something.
          </div>
        )}

        {items.map((item, i) => (
          <div key={item.id} style={{
            padding: '20px 48px',
            borderBottom: '1px solid #1a1a1a',
            display: 'flex',
            alignItems: 'center',
            gap: 20,
            transition: 'background 0.15s',
          }}
          onMouseEnter={e => (e.currentTarget.style.background = '#0a0a0a')}
          onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
          >
            {/* Image or index */}
            {item.image ? (
              <img src={item.image} alt={item.name}
                style={{ width: 44, height: 44, objectFit: 'cover', flexShrink: 0 }} />
            ) : (
              <div style={{
                width: 44, height: 44, background: '#111', flexShrink: 0,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 11, color: '#333', fontWeight: 500
              }}>
                {String(i + 1).padStart(2, '0')}
              </div>
            )}

            {/* Name + price */}
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13, color: '#fff', letterSpacing: '0.01em', marginBottom: 4 }}>
                {item.name}
              </div>
              <div style={{ fontSize: 11, color: '#555', letterSpacing: '0.05em' }}>
                {item.price}
              </div>
            </div>

            {/* Platforms + status */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 6, flexShrink: 0 }}>
              <div style={{ display: 'flex', gap: 6 }}>
                {item.platforms?.map((p: string) => (
                  <span key={p} style={{
                    fontSize: 9, letterSpacing: '0.12em', textTransform: 'uppercase',
                    color: '#555', border: '1px solid #222', padding: '2px 6px',
                  }}>
                    {p}
                  </span>
                ))}
              </div>
              <span style={{
                fontSize: 9, letterSpacing: '0.12em', textTransform: 'uppercase',
                color: item.status === 'Synced' ? '#2ecc71' : item.status === 'Failed' ? '#e74c3c' : '#f39c12',
              }}>
                {item.status}
              </span>
            </div>
          </div>
        ))}

        {isRefreshing && (
          <div style={{ padding: '20px 48px', fontSize: 11, color: '#444', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
            Syncing...
          </div>
        )}
      </div>
    </div>
  );
}
