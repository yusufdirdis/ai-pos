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
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '32px 48px', display: 'flex', flexDirection: 'column', gap: 24 }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
            {msg.role === 'assistant' && (
              <div style={{ marginRight: 12, marginTop: 2 }}>
                <span style={{ fontSize: 9, letterSpacing: '0.15em', textTransform: 'uppercase', color: '#444' }}>AI</span>
              </div>
            )}
            <div style={{
              maxWidth: '72%',
              fontSize: 13,
              lineHeight: 1.65,
              color: msg.role === 'user' ? '#000' : '#ccc',
              background: msg.role === 'user' ? '#fff' : 'transparent',
              padding: msg.role === 'user' ? '10px 16px' : '0',
              letterSpacing: '0.01em',
            }}>
              {msg.content}
            </div>
          </div>
        ))}

        {isLoading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 9, letterSpacing: '0.15em', textTransform: 'uppercase', color: '#444', marginRight: 4 }}>AI</span>
            <Loader2 size={12} style={{ animation: 'spin 1s linear infinite', color: '#555' }} />
            <span style={{ fontSize: 12, color: '#444', letterSpacing: '0.05em' }}>Processing...</span>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input area */}
      <div style={{ borderTop: '1px solid #1a1a1a', padding: '20px 48px' }}>
        
        {/* Filters */}
        <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
          <button 
            onClick={() => setActivePlatform(null)}
            style={{ fontSize: 9, letterSpacing: '0.1em', textTransform: 'uppercase', padding: '4px 8px', border: '1px solid #333', background: activePlatform === null ? '#fff' : 'transparent', color: activePlatform === null ? '#000' : '#888', cursor: 'pointer' }}>
            All
          </button>
          {['Square', 'UberEats', 'DoorDash'].map(p => (
            <button 
              key={p} onClick={() => setActivePlatform(p)}
              style={{ fontSize: 9, letterSpacing: '0.1em', textTransform: 'uppercase', padding: '4px 8px', border: '1px solid #333', background: activePlatform === p ? '#fff' : 'transparent', color: activePlatform === p ? '#000' : '#888', cursor: 'pointer' }}>
              {p}
            </button>
          ))}
          <button style={{ marginLeft: 'auto', fontSize: 9, letterSpacing: '0.1em', textTransform: 'uppercase', padding: '4px 8px', border: '1px dotted #333', background: 'transparent', color: '#555', cursor: 'help' }} title="CRM & Data Predictor (Coming Soon)">
            Data CRM
          </button>
        </div>
        {previewUrl && (
          <div style={{ marginBottom: 12, position: 'relative', display: 'inline-block' }}>
            <img src={previewUrl} alt="Preview" style={{ width: 48, height: 48, objectFit: 'cover' }} />
            <button onClick={clearFile} style={{
              position: 'absolute', top: -6, right: -6,
              background: '#fff', border: 'none', cursor: 'pointer',
              width: 16, height: 16, display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <X size={10} color="#000" />
            </button>
          </div>
        )}
        <form onSubmit={e => { e.preventDefault(); sendMessage(); }}
          style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
          <input type="file" accept="image/*" className="hidden" ref={fileInputRef} onChange={handleFileSelect} />
          <button type="button" onClick={() => fileInputRef.current?.click()}
            style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0, color: '#444', display: 'flex', alignItems: 'center' }}
            title="Attach image">
            <ImagePlus size={16} />
          </button>
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="e.g. Remove the spicy chicken sandwich..."
            style={{
              flex: 1, background: 'none', border: 'none', borderBottom: '1px solid #2a2a2a',
              color: '#fff', fontSize: 13, padding: '8px 0', outline: 'none',
              letterSpacing: '0.01em',
            }}
          />
          <button type="submit" disabled={isLoading || (!input.trim() && !selectedFile)}
            style={{
              background: 'none', border: 'none', cursor: 'pointer', color: isLoading ? '#333' : '#fff',
              display: 'flex', alignItems: 'center', padding: 0,
            }}>
            <Send size={14} />
          </button>
        </form>
      </div>
    </div>
  );
}
