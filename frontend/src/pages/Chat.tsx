import { useState } from 'react';
import { Send, Bot, User } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: string[];
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello. I am the AI Medical Assistant. How can I help you understand your medical reports or health information today? \n\n**Please remember that I provide information for educational purposes only and am not a substitute for professional medical advice.**'
    }
  ]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;
    
    const newMsg: Message = { id: Date.now().toString(), role: 'user', content: input };
    setMessages(prev => [...prev, newMsg]);
    setInput('');
    
    // Simulate AI response
    setTimeout(() => {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'This is a simulated response based on trusted medical knowledge bases using RAG. In a real environment, this would summarize the uploaded document and answer your specific query with context.',
        citations: ['CDC Guidelines on Blood Pressure', 'WHO Health Standards']
      }]);
    }, 1500);
  };

  return (
    <div className="h-[calc(100vh-12rem)] flex flex-col bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'assistant' && (
              <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center shrink-0 mt-1">
                <Bot className="h-5 w-5 text-primary-600" />
              </div>
            )}
            
            <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
              msg.role === 'user' 
                ? 'bg-primary-600 text-white rounded-tr-sm' 
                : 'bg-slate-100 text-slate-800 rounded-tl-sm'
            }`}>
              <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
              
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-200/50">
                  <p className="text-xs font-semibold text-slate-500 uppercase mb-1">Sources:</p>
                  <ul className="text-xs text-slate-600 space-y-1">
                    {msg.citations.map((c, i) => (
                      <li key={i} className="flex items-center gap-1">
                        <span className="h-1 w-1 bg-slate-400 rounded-full inline-block"></span>
                        {c}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {msg.role === 'user' && (
              <div className="h-8 w-8 rounded-full bg-slate-200 flex items-center justify-center shrink-0 mt-1">
                <User className="h-5 w-5 text-slate-600" />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-slate-200 bg-slate-50">
        <div className="flex gap-2">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask a question about your health report..."
            className="flex-1 bg-white border border-slate-300 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
          />
          <button 
            onClick={handleSend}
            disabled={!input.trim()}
            className="bg-primary-600 hover:bg-primary-700 disabled:bg-slate-300 text-white p-2 w-12 rounded-xl flex items-center justify-center transition-colors shadow-sm"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
