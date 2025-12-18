import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, MessageSquare, Activity, Terminal, Shield, Settings, Sparkles } from 'lucide-react';
import { cn } from '../utils';

interface NavItemProps {
  to: string;
  icon: React.ElementType;
  label: string;
}

function NavItem({ to, icon: Icon, label }: NavItemProps) {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link
      to={to}
      className={cn('nav-item', isActive && 'active')}
    >
      <Icon size={18} className={cn(isActive ? 'text-foreground' : 'text-muted-foreground')} />
      <span>{label}</span>
    </Link>
  );
}

function NavSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1">
      <h3 className="px-3 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/60 mb-2">
        {title}
      </h3>
      {children}
    </div>
  );
}

export default function Sidebar() {
  return (
    <aside className="w-[260px] h-full border-r border-border/40 bg-background flex flex-col shrink-0">
      {/* Brand Header */}
      <div className="h-16 flex items-center gap-3 px-5 border-b border-border/40">
        <div className="relative">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <Sparkles size={18} className="text-white" />
          </div>
          <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 rounded-full border-2 border-background" />
        </div>
        <div>
          <h1 className="text-sm font-bold tracking-tight">Aura Orchestra</h1>
          <p className="text-[10px] text-muted-foreground">AI Orchestration Platform</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-6 px-3 space-y-6">
        <NavSection title="Main">
          <NavItem to="/" icon={LayoutDashboard} label="Overview" />
          <NavItem to="/chat" icon={MessageSquare} label="Assistant" />
        </NavSection>

        <NavSection title="System">
          <NavItem to="/monitoring" icon={Activity} label="Monitoring" />
          <NavItem to="/jobs" icon={Terminal} label="Jobs" />
          <NavItem to="/auditor" icon={Shield} label="Auditor" />
        </NavSection>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-border/40">
        <button className="nav-item w-full justify-start">
          <Settings size={18} />
          <span>Settings</span>
        </button>

        <div className="mt-4 px-3 py-3 rounded-lg bg-muted/30 border border-border/30">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-zinc-700 to-zinc-800 flex items-center justify-center text-xs font-bold">
              OP
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium truncate">Operator</p>
              <p className="text-[10px] text-muted-foreground truncate">admin@aura.internal</p>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
