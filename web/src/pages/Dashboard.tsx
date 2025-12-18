import { useState, useEffect } from 'react';
import { Activity, Zap, Server, DollarSign, TrendingUp, Shield, Cpu, Play, FileText, AlertTriangle, ChevronRight } from 'lucide-react';
import EventPanel from '../components/EventPanel';
import { cn } from '../utils';
import { motion, AnimatePresence } from 'framer-motion';

// ============================================
// ANIMATED NUMBER COUNTER
// ============================================

function AnimatedCounter({ value, duration = 1.5 }: { value: number; duration?: number }) {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    let start = 0;
    const end = value;
    const increment = end / (duration * 60);
    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, 1000 / 60);
    return () => clearInterval(timer);
  }, [value, duration]);
  
  return <span>{count.toLocaleString()}</span>;
}

// ============================================
// ORBITAL STATUS RING
// ============================================

function OrbitalStatusRing() {
  const nodes = [
    { id: 1, angle: 0, status: 'active' },
    { id: 2, angle: 45, status: 'active' },
    { id: 3, angle: 90, status: 'idle' },
    { id: 4, angle: 135, status: 'active' },
    { id: 5, angle: 180, status: 'idle' },
    { id: 6, angle: 225, status: 'active' },
    { id: 7, angle: 270, status: 'offline' },
    { id: 8, angle: 315, status: 'active' },
  ];

  return (
    <div className="relative w-32 h-32">
      {/* Outer rotating ring */}
      <motion.div
        className="absolute inset-0 rounded-full border border-accent/20"
        animate={{ rotate: 360 }}
        transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
      />
      
      {/* Inner pulsing core */}
      <div className="absolute inset-4 rounded-full bg-gradient-to-br from-accent/30 to-accent/10 flex items-center justify-center">
        <motion.div
          className="w-12 h-12 rounded-full bg-accent/40 blur-sm"
          animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.8, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
        <div className="absolute w-8 h-8 rounded-full bg-accent flex items-center justify-center">
          <Shield size={16} className="text-background" />
        </div>
      </div>
      
      {/* Orbiting nodes */}
      {nodes.map((node) => {
        const radians = (node.angle * Math.PI) / 180;
        const x = 56 * Math.cos(radians);
        const y = 56 * Math.sin(radians);
        const statusColor = {
          active: 'bg-emerald-500',
          idle: 'bg-amber-500',
          offline: 'bg-zinc-600',
        }[node.status];
        
        return (
          <motion.div
            key={node.id}
            className={cn('absolute w-3 h-3 rounded-full', statusColor)}
            style={{ left: `calc(50% + ${x}px - 6px)`, top: `calc(50% + ${y}px - 6px)` }}
            animate={{ scale: node.status === 'active' ? [1, 1.3, 1] : 1 }}
            transition={{ duration: 1.5, repeat: Infinity, delay: node.id * 0.1 }}
          >
            {node.status === 'active' && (
              <div className={cn('absolute inset-0 rounded-full animate-ping', statusColor, 'opacity-50')} />
            )}
          </motion.div>
        );
      })}
    </div>
  );
}

// ============================================
// BENTO HERO STAT (Large 2x2)
// ============================================

function BentoHeroStat({ delay = 0 }: { delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay: delay * 0.1 }}
      className="relative col-span-2 row-span-2 rounded-2xl overflow-hidden group"
    >
      {/* Animated gradient border */}
      <div className="absolute inset-0 rounded-2xl p-[1px] bg-gradient-to-br from-accent via-purple-500 to-pink-500 animate-gradient-rotate">
        <div className="absolute inset-[1px] rounded-2xl bg-card" />
      </div>
      
      {/* Aurora background */}
      <div className="absolute inset-0 overflow-hidden rounded-2xl">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-conic from-accent/20 via-transparent to-accent/10 animate-spin-slow opacity-50" />
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-conic from-purple-500/15 via-transparent to-pink-500/10 animate-spin-slow-reverse opacity-50" />
      </div>
      
      {/* Content */}
      <div className="relative h-full p-8 flex flex-col justify-between z-10">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs font-medium uppercase tracking-widest text-muted-foreground mb-1">Active Jobs</p>
            <p className="text-6xl font-bold tracking-tight bg-gradient-to-r from-foreground via-foreground to-muted-foreground bg-clip-text text-transparent">
              <AnimatedCounter value={47} duration={1.2} />
            </p>
            <p className="text-sm text-muted-foreground mt-2">Processing across 8 nodes</p>
          </div>
          <OrbitalStatusRing />
        </div>
        
        <div className="flex items-center gap-6 pt-4 border-t border-border/30">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className="text-xs text-muted-foreground">6 Active</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-amber-500" />
            <span className="text-xs text-muted-foreground">1 Idle</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-zinc-600" />
            <span className="text-xs text-muted-foreground">1 Offline</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// ============================================
// BENTO STAT CARD (Small)
// ============================================

interface BentoStatProps {
  title: string;
  value: string;
  trend?: { value: string; positive: boolean };
  icon: React.ElementType;
  delay?: number;
  accent?: boolean;
}

function BentoStat({ title, value, trend, icon: Icon, delay = 0, accent }: BentoStatProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: delay * 0.1 }}
      className={cn(
        'glass-panel p-5 group cursor-default',
        accent && 'ring-1 ring-accent/30'
      )}
    >
      <div className="flex items-center justify-between mb-3">
        <div className={cn(
          'p-2 rounded-lg transition-all duration-300',
          accent ? 'bg-accent/20 text-accent' : 'bg-muted/50 text-muted-foreground group-hover:text-foreground'
        )}>
          <Icon size={16} />
        </div>
        {trend && (
          <span className={cn(
            'text-xs font-semibold px-2 py-0.5 rounded-full',
            trend.positive ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
          )}>
            {trend.positive ? '↑' : '↓'} {trend.value}
          </span>
        )}
      </div>
      <p className="text-2xl font-bold tracking-tight">{value}</p>
      <p className="text-xs text-muted-foreground mt-1">{title}</p>
    </motion.div>
  );
}

// ============================================
// NEURAL NETWORK VISUALIZATION
// ============================================

function NeuralNetwork({ delay = 0 }: { delay?: number }) {
  const nodes = [
    { id: 'ollama', x: 30, y: 25, name: 'Ollama', model: 'llama3:8b', status: 'busy' },
    { id: 'gpt', x: 70, y: 25, name: 'GPT-4o', model: 'gpt-4o', status: 'idle' },
    { id: 'claude', x: 50, y: 75, name: 'Claude', model: 'claude-3', status: 'busy' },
  ];
  
  const connections = [
    { from: 'ollama', to: 'gpt' },
    { from: 'gpt', to: 'claude' },
    { from: 'claude', to: 'ollama' },
  ];

  const statusColors = {
    busy: { bg: 'bg-amber-500', ring: 'ring-amber-500/30', glow: 'shadow-amber-500/40' },
    idle: { bg: 'bg-emerald-500', ring: 'ring-emerald-500/30', glow: 'shadow-emerald-500/40' },
    offline: { bg: 'bg-zinc-600', ring: 'ring-zinc-600/30', glow: '' },
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: delay * 0.1 }}
      className="glass-panel overflow-hidden"
    >
      <div className="px-5 py-4 border-b border-border/30 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Cpu size={16} className="text-accent" />
          <h3 className="text-sm font-semibold">Neural Network</h3>
        </div>
        <span className="text-xs text-muted-foreground">3 models</span>
      </div>
      
      <div className="relative h-48 p-4">
        {/* Connection lines */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none">
          {connections.map((conn, i) => {
            const from = nodes.find(n => n.id === conn.from)!;
            const to = nodes.find(n => n.id === conn.to)!;
            return (
              <motion.line
                key={i}
                x1={`${from.x}%`}
                y1={`${from.y}%`}
                x2={`${to.x}%`}
                y2={`${to.y}%`}
                stroke="hsl(var(--border))"
                strokeWidth="1"
                strokeDasharray="4 4"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 1, delay: 0.5 + i * 0.2 }}
              />
            );
          })}
        </svg>
        
        {/* Nodes */}
        {nodes.map((node, i) => {
          const colors = statusColors[node.status as keyof typeof statusColors];
          return (
            <motion.div
              key={node.id}
              className="absolute transform -translate-x-1/2 -translate-y-1/2"
              style={{ left: `${node.x}%`, top: `${node.y}%` }}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.3, delay: 0.3 + i * 0.1 }}
            >
              <div className={cn(
                'relative w-14 h-14 rounded-xl flex flex-col items-center justify-center',
                'bg-card border border-border/50 ring-2',
                colors.ring,
                colors.glow && `shadow-lg ${colors.glow}`
              )}>
                <motion.div
                  className={cn('w-2 h-2 rounded-full mb-1', colors.bg)}
                  animate={node.status === 'busy' ? { scale: [1, 1.3, 1] } : {}}
                  transition={{ duration: 1, repeat: Infinity }}
                />
                <span className="text-[10px] font-medium">{node.name}</span>
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}

// ============================================
// ACTIVITY STREAM (Enhanced)
// ============================================

function ActivityStream({ delay = 0 }: { delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: delay * 0.1 }}
      className="glass-panel flex flex-col h-full"
    >
      <div className="px-5 py-4 border-b border-border/30 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <Activity size={16} className="text-accent" />
          <h3 className="text-sm font-semibold">Live Activity</h3>
        </div>
        <div className="flex items-center gap-2">
          <motion.div
            className="w-2 h-2 rounded-full bg-emerald-500"
            animate={{ scale: [1, 1.3, 1], opacity: [1, 0.7, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
          <span className="text-xs text-muted-foreground">Live</span>
        </div>
      </div>
      
      <div className="flex-1 overflow-hidden">
        <EventPanel />
      </div>
    </motion.div>
  );
}

// ============================================
// FLOATING ACTION ORB
// ============================================

function FloatingActionOrb() {
  const [isOpen, setIsOpen] = useState(false);
  
  const actions = [
    { icon: Play, label: 'Submit PRD', color: 'bg-emerald-500' },
    { icon: FileText, label: 'View Logs', color: 'bg-blue-500' },
    { icon: AlertTriangle, label: 'Emergency', color: 'bg-red-500' },
  ];
  
  return (
    <div className="fixed bottom-8 right-8 z-50">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="absolute bottom-16 right-0 flex flex-col gap-3 items-end"
          >
            {actions.map((action, i) => (
              <motion.button
                key={action.label}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: i * 0.05 }}
                className="flex items-center gap-3 px-4 py-2 rounded-full bg-card border border-border/50 hover:border-accent/50 transition-colors group"
              >
                <span className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">{action.label}</span>
                <div className={cn('p-2 rounded-full', action.color)}>
                  <action.icon size={14} className="text-white" />
                </div>
              </motion.button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
      
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className="relative w-14 h-14 rounded-full bg-accent flex items-center justify-center shadow-lg shadow-accent/30 hover:shadow-accent/50 transition-shadow"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <motion.div
          className="absolute inset-0 rounded-full bg-accent"
          animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
        <motion.div
          animate={{ rotate: isOpen ? 45 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronRight size={24} className="text-background rotate-[-90deg]" />
        </motion.div>
      </motion.button>
    </div>
  );
}

// ============================================
// MAIN DASHBOARD COMPONENT
// ============================================

export default function Dashboard() {
  return (
    <div className="h-full overflow-y-auto bg-gradient-radial">
      <div className="min-h-full bg-dot-pattern">
        <div className="max-w-7xl mx-auto p-8 space-y-8">
          
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="flex items-center justify-between"
          >
            <div>
              <h1 className="text-3xl font-bold tracking-tight mb-1 bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">
                Mission Control
              </h1>
              <p className="text-sm text-muted-foreground">Real-time orchestration & system telemetry</p>
            </div>
            
            <div className="flex items-center gap-2 px-4 py-2 rounded-full glass-panel">
              <motion.div
                className="w-2 h-2 rounded-full bg-emerald-500"
                animate={{ scale: [1, 1.3, 1], opacity: [1, 0.7, 1] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              />
              <span className="text-xs font-medium">All Systems Operational</span>
            </div>
          </motion.div>

          {/* Bento Grid */}
          <div className="grid grid-cols-4 gap-4 auto-rows-[140px]">
            <BentoHeroStat delay={1} />
            
            <BentoStat
              title="Total Completed"
              value="1,284"
              trend={{ value: '12%', positive: true }}
              icon={Zap}
              delay={2}
            />
            <BentoStat
              title="Active Nodes"
              value="8/12"
              icon={Server}
              delay={3}
              accent
            />
            <BentoStat
              title="Est. Cost (MTD)"
              value="$24.50"
              trend={{ value: '3%', positive: false }}
              icon={DollarSign}
              delay={4}
            />
            <BentoStat
              title="Uptime (30d)"
              value="99.9%"
              icon={TrendingUp}
              delay={5}
            />
          </div>

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6" style={{ minHeight: '400px' }}>
            <div className="lg:col-span-2 flex flex-col">
              <ActivityStream delay={6} />
            </div>
            
            <div className="space-y-6">
              <NeuralNetwork delay={7} />
            </div>
          </div>

        </div>
      </div>
      
      <FloatingActionOrb />
    </div>
  );
}
