"use client";

import { useState } from 'react';
import ChatBox from '@/components/ChatBox';
import MenuDashboard from '@/components/MenuDashboard';

export default function Home() {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleMenuUpdate = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 2000);
  };

  return (
    <main className="min-h-screen p-8 lg:p-24 max-w-7xl mx-auto">
      <div className="mb-12 text-center">
        <h1 className="text-4xl lg:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400 mb-4">
          MenuFlow
        </h1>
        <p className="text-lg text-slate-400 max-w-2xl mx-auto">
          Manage your restaurant menu across POS and Delivery platforms instantly using natural language AI.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">AI Assistant</h2>
            <div className="flex items-center gap-2 text-xs text-emerald-400">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              System Online
            </div>
          </div>
          <ChatBox onMenuUpdate={handleMenuUpdate} />
        </div>
        
        <div className="flex flex-col gap-4">
           <div className="flex items-center justify-between mb-2">
            <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Real-time Sync</h2>
          </div>
          <MenuDashboard isRefreshing={isRefreshing} />
        </div>
      </div>
    </main>
  );
}
