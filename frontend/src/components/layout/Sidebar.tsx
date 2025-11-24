import { NavLink } from "@/components/NavLink";
import { 
  LayoutDashboard, 
  Brain, 
  BarChart3, 
  Calendar, 
  Users, 
  Webhook, 
  Activity,
  Settings,
  Zap
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: 'Dashboard', to: '/', icon: LayoutDashboard },
  { name: 'AI Intelligence', to: '/intelligence', icon: Brain },
  { name: 'Analytics', to: '/analytics', icon: BarChart3 },
  { name: 'Events', to: '/events', icon: Calendar },
  { name: 'Teams', to: '/teams', icon: Users },
  { name: 'Webhooks', to: '/webhooks', icon: Webhook },
  { name: 'Actions', to: '/actions', icon: Activity },
  { name: 'Settings', to: '/settings', icon: Settings },
];

export function Sidebar() {
  return (
    <div className="flex h-screen w-64 flex-col border-r border-sidebar-border bg-sidebar">
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 border-b border-sidebar-border px-6">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary glow-primary">
          <Zap className="h-6 w-6 text-primary-foreground" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-sidebar-foreground">FlowSentinel</h1>
          <p className="text-xs text-muted-foreground">AI Project Intelligence</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.to}
            end
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all",
              "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-foreground"
            )}
            activeClassName="bg-sidebar-accent text-sidebar-foreground shadow-sm"
          >
            <item.icon className="h-5 w-5" />
            {item.name}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-sidebar-border p-4">
        <div className="glass-card rounded-lg p-3">
          <p className="text-xs font-medium text-sidebar-foreground">Powered by</p>
          <p className="text-sm font-bold text-primary">IBM watsonx.ai</p>
          <p className="text-xs text-muted-foreground mt-0.5">Granite 3 8B Instruct</p>
        </div>
      </div>
    </div>
  );
}
