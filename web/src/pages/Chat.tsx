import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../utils';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function Chat() {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hello! I'm Aura, your AI orchestration assistant. I can help you manage clusters, analyze system performance, and troubleshoot issues. What would you like to do today?",
      timestamp: new Date(),
    },
  ]);
  
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const responses = [
        "I've analyzed the cluster metrics. All nodes are operating within normal parameters. Would you like me to generate a detailed report?",
        "Processing your request... I've identified 3 optimization opportunities in the current job queue. Shall I apply them automatically?",
        "The system telemetry shows healthy status across all services. The auditor detected no anomalies in the last 24 hours.",
      ];
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: responses[Math.floor(Math.random() * responses.length)],
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, aiMessage]);
      setIsLoading(false);
    }, 1500);
  };

  return (
    <div className="flex flex-col h-full bg-gradient-radial">
      <div className="flex-1 bg-dot-pattern relative">
        {/* Header */}
        <div className="absolute top-0 left-0 right-0 h-16 border-b border-border/40 bg-background/80 backdrop-blur-xl z-10 flex items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
              <Sparkles size={16} className="text-white" />
            </div>
            <div>
              <h1 className="text-sm font-semibold">Aura Assistant</h1>
              <p className="text-[10px] text-muted-foreground">AI-powered orchestration</p>
            </div>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted/30 border border-border/40">
            <div className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className="text-xs text-muted-foreground">Online</span>
          </div>
        </div>

        {/* Messages */}
        <div className="h-full overflow-y-auto pt-20 pb-32">
          <div className="max-w-3xl mx-auto px-6 py-8 space-y-6">
            <AnimatePresence mode="popLayout">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className={cn(
                    'flex gap-4',
                    message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                  )}
                >
                  {/* Avatar */}
                  <div className={cn(
                    'w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ring-1 ring-inset',
                    message.role === 'assistant'
                      ? 'bg-gradient-to-br from-indigo-500 to-purple-600 ring-white/10'
                      : 'bg-muted ring-border'
                  )}>
                    {message.role === 'assistant' ? (
                      <Bot size={16} className="text-white" />
                    ) : (
                      <User size={16} className="text-muted-foreground" />
                    )}
                  </div>

                  {/* Message Bubble */}
                  <div className={cn(
                    'max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed',
                    message.role === 'assistant'
                      ? 'bg-muted/50 border border-border/40 text-foreground rounded-tl-md'
                      : 'bg-indigo-600 text-white rounded-tr-md shadow-lg shadow-indigo-500/20'
                  )}>
                    {message.content}
                  </div>
                </motion.div>
              ))}

              {/* Loading indicator */}
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex gap-4"
                >
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center ring-1 ring-inset ring-white/10">
                    <Bot size={16} className="text-white" />
                  </div>
                  <div className="bg-muted/50 border border-border/40 rounded-2xl rounded-tl-md px-4 py-3">
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Loader2 size={14} className="animate-spin" />
                      <span className="text-sm">Thinking...</span>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            <div ref={scrollRef} />
          </div>
        </div>

        {/* Input */}
        <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-background via-background to-transparent">
          <div className="max-w-3xl mx-auto">
            <form onSubmit={handleSubmit} className="relative">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask Aura anything..."
                disabled={isLoading}
                className="w-full bg-muted/30 border border-border/40 rounded-2xl px-5 py-4 pr-14 text-sm placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="absolute right-2 top-2 p-2.5 rounded-xl bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-indigo-500/20"
              >
                <Send size={16} />
              </button>
            </form>
            <p className="text-center text-[10px] text-muted-foreground/50 mt-3">
              Aura can make mistakes. Verify critical system operations.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
