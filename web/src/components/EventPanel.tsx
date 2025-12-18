import { useEffect, useState, useRef } from 'react';
import { format } from 'date-fns';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../utils';

interface Event {
  id: number;
  actor: string;
  action: string;
  details: any;
  ts: string;
}

const actionColors: Record<string, string> = {
  'ALERT': 'badge-error',
  'JOB_START': 'badge-info',
  'JOB_END': 'badge-success',
  'ANOMALY': 'badge-warning',
  'default': 'badge-neutral',
};

export default function EventPanel() {
  const [events, setEvents] = useState<Event[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const evtSource = new EventSource('http://localhost:8001/events');
    
    evtSource.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        setEvents(prev => [...prev.slice(-100), data]); // Keep last 100 events
      } catch {}
    };
    
    return () => evtSource.close();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events]);

  if (events.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-muted-foreground/50 p-8">
        <div className="relative mb-4">
          <div className="w-3 h-3 rounded-full bg-indigo-500/50 animate-ping" />
          <div className="absolute inset-0 w-3 h-3 rounded-full bg-indigo-500" />
        </div>
        <p className="text-sm font-medium">Listening for events...</p>
        <p className="text-xs text-muted-foreground/40 mt-1">Telemetry will appear here</p>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto p-4 space-y-1">
      <AnimatePresence mode="popLayout">
        {events.map((evt) => (
          <motion.div
            key={evt.id}
            initial={{ opacity: 0, x: -20, height: 0 }}
            animate={{ opacity: 1, x: 0, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="group"
          >
            <div className="flex items-center gap-4 p-3 rounded-lg hover:bg-muted/30 transition-all border border-transparent hover:border-border/30">
              {/* Timestamp */}
              <div className="w-14 shrink-0">
                <span className="text-[10px] font-mono text-muted-foreground/60">
                  {format(new Date(evt.ts), 'HH:mm:ss')}
                </span>
              </div>

              {/* Actor */}
              <div className="w-20 shrink-0">
                <span className="text-xs font-semibold uppercase tracking-wide text-foreground/80">
                  {evt.actor}
                </span>
              </div>

              {/* Action Badge */}
              <div className="w-24 shrink-0">
                <span className={cn('badge', actionColors[evt.action] || actionColors.default)}>
                  {evt.action}
                </span>
              </div>

              {/* Details */}
              <div className="flex-1 min-w-0">
                <span className="text-xs text-muted-foreground truncate block font-mono group-hover:text-foreground/70 transition-colors">
                  {typeof evt.details === 'object' ? JSON.stringify(evt.details) : evt.details}
                </span>
              </div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
      <div ref={bottomRef} />
    </div>
  );
}
