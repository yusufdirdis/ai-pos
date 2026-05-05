"use client";

import { useState, useRef, useEffect } from 'react';
import { Send, ImagePlus, X, Loader2 } from 'lucide-react';

type Message = { role: 'user' | 'assistant', content: string };

export default function ChatBox({ onMenuUpdate, activePlatform, setActivePlatform }: { onMenuUpdate: () => void, activePlatform: string | null, setActivePlatform: (val: string | null) => void }) {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: "Ready. Add, update, or remove items across Square, Clover, and Uber Eats." }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() && !selectedFile) return;
    const userMsg = input.trim();
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMsg + (selectedFile ? ' [Image attached]' : '')
    }]);
    setInput('');
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append('message', userMsg || 'Analyze this image');
      if (activePlatform) formData.append('platform_filter', activePlatform);
      if (selectedFile) formData.append('image', selectedFile);
      // Send last 6 messages as conversation history for context
      const history = messages.slice(-6).map(m => `${m.role}: ${m.content}`).join('\n');
      formData.append('history', history);

      const res = await fetch('http://localhost:8000/api/items/chat', { method: 'POST', body: formData });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
      clearFile();
      onMenuUpdate();
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "Connection failed. Make sure the backend is running at localhost:8000."
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 md:px-12 md:py-8 flex flex-col gap-4 md:gap-6">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'assistant' && (
              <div className="mr-3 mt-1 shrink-0">
                <span className="text-[9px] tracking-[0.15em] uppercase text-[#444]">AI</span>
              </div>
            )}
            <div className={`max-w-[85%] md:max-w-[72%] text-[13px] leading-relaxed tracking-[0.01em] ${
              msg.role === 'user' ? 'text-black bg-white px-4 py-2.5' : 'text-[#ccc] bg-transparent p-0'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex items-center gap-2.5">
            <span className="text-[9px] tracking-[0.15em] uppercase text-[#444] mr-1">AI</span>
            <Loader2 size={12} className="animate-spin text-[#555]" />
            <span className="text-[12px] text-[#444] tracking-[0.05em]">Processing...</span>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-[#1a1a1a] px-4 py-4 md:px-16 md:py-7 shrink-0 bg-black">
        
        {/* Filters */}
        <div className="flex gap-2 md:gap-3 mb-4 overflow-x-auto no-scrollbar pb-1">
          <button 
            onClick={() => setActivePlatform(null)}
            className={`shrink-0 text-[9px] tracking-[0.1em] uppercase px-2 py-1 border border-[#333] cursor-pointer transition-colors ${activePlatform === null ? 'bg-white text-black' : 'bg-transparent text-[#888]'}`}>
            All
          </button>
          {['Square', 'UberEats', 'DoorDash'].map(p => (
            <button 
              key={p} onClick={() => setActivePlatform(p)}
              className={`shrink-0 text-[9px] tracking-[0.1em] uppercase px-2 py-1 border border-[#333] cursor-pointer transition-colors ${activePlatform === p ? 'bg-white text-black' : 'bg-transparent text-[#888]'}`}>
              {p}
            </button>
          ))}
          <button className="shrink-0 ml-auto text-[9px] tracking-[0.1em] uppercase px-2 py-1 border border-dotted border-[#333] bg-transparent text-[#555] cursor-help" title="CRM & Data Predictor (Coming Soon)">
            Data CRM
          </button>
        </div>

        {previewUrl && (
          <div className="mb-3 relative inline-block">
            <img src={previewUrl} alt="Preview" className="w-12 h-12 object-cover" />
            <button onClick={clearFile} className="absolute -top-1.5 -right-1.5 bg-white border-none cursor-pointer w-4 h-4 flex items-center justify-center rounded-none">
              <X size={10} color="#000" />
            </button>
          </div>
        )}

        <form onSubmit={e => { e.preventDefault(); sendMessage(); }} className="flex gap-3 md:gap-4 items-center">
          <input type="file" accept="image/*" className="hidden" ref={fileInputRef} onChange={handleFileSelect} />
          <button type="button" onClick={() => fileInputRef.current?.click()} className="bg-none border-none cursor-pointer p-0 text-[#444] flex items-center shrink-0" title="Attach image">
            <ImagePlus size={16} />
          </button>
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="e.g. Remove the spicy chicken sandwich..."
            className="flex-1 bg-transparent border-none border-b border-[#2a2a2a] text-white text-[13px] py-2 outline-none tracking-[0.01em] min-w-0 w-full rounded-none"
          />
          <button type="submit" disabled={isLoading || (!input.trim() && !selectedFile)} className={`bg-none border-none cursor-pointer flex items-center p-0 shrink-0 ${isLoading ? 'text-[#333]' : 'text-white'}`}>
            <Send size={14} />
          </button>
        </form>
      </div>
    </div>
  );
}
