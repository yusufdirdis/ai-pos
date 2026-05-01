"use client";

import { motion } from 'framer-motion';
import { RefreshCw, CheckCircle2, Box } from 'lucide-react';

export default function MenuDashboard({ isRefreshing }: { isRefreshing: boolean }) {
  // Mock data for demonstration of synced state
  const recentItems = [
    { id: 1, name: "Spicy Chicken Sandwich", price: "$8.99", status: "Synced", platforms: ["Square", "Clover"] },
    { id: 2, name: "Large Fries", price: "$3.49", status: "Synced", platforms: ["Square"] }
  ];

  return (
    <div className="glass-panel rounded-2xl p-6 h-[600px] flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-semibold text-white">Live Menu Sync</h2>
          <p className="text-sm text-slate-400">Central Database Overview</p>
        </div>
        <button className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
          <RefreshCw className={`w-5 h-5 text-slate-300 ${isRefreshing ? 'animate-spin text-blue-400' : ''}`} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3">
        {recentItems.map((item, i) => (
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            key={item.id} 
            className="p-4 rounded-xl bg-white/5 border border-white/10 flex items-center justify-between group hover:bg-white/10 transition-colors"
          >
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center">
                <Box className="w-5 h-5 text-indigo-400" />
              </div>
              <div>
                <h3 className="text-white font-medium">{item.name}</h3>
                <p className="text-xs text-emerald-400">{item.price}</p>
              </div>
            </div>
            
            <div className="flex flex-col items-end gap-1">
              <div className="flex items-center gap-1 text-xs text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-md">
                <CheckCircle2 className="w-3 h-3" />
                {item.status}
              </div>
              <div className="flex gap-1">
                {item.platforms.map(p => (
                  <span key={p} className="text-[10px] text-slate-400 bg-black/30 px-1.5 py-0.5 rounded">
                    {p}
                  </span>
                ))}
              </div>
            </div>
          </motion.div>
        ))}
        
        {isRefreshing && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 flex justify-center items-center"
          >
             <span className="text-sm text-blue-400 animate-pulse flex items-center gap-2">
               <RefreshCw className="w-4 h-4 animate-spin" /> Fetching recent DB updates...
             </span>
          </motion.div>
        )}
        
        <div className="p-8 text-center text-slate-500 text-sm border border-dashed border-white/10 rounded-xl mt-4">
          Use the AI Chatbot to add or update menu items. They will appear here when synced.
        </div>
      </div>
    </div>
  );
}
