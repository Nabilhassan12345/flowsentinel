import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import type { ProjectState, Event, AgentStatus, AnalyticsSummary } from "@/lib/api";
import { StatusIndicator } from "@/components/dashboard/StatusIndicator";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { EventFeed } from "@/components/dashboard/EventFeed";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Activity, 
  AlertCircle, 
  TrendingUp, 
  Users, 
  Play, 
  Pause, 
  RefreshCw,
  Download,
  Sparkles
} from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { formatDistanceToNow } from "date-fns";

export default function Dashboard() {
  // Fetch project state
  const { data: state } = useQuery<ProjectState>({
    queryKey: ['projectState'],
    queryFn: async () => {
      const { data } = await apiClient.get('/state/latest');
      return data;
    },
    refetchInterval: 30000, // Refresh every 30s
  });

  // Fetch recent events
  const { data: eventsData } = useQuery<{ events: Event[] }>({
    queryKey: ['recentEvents'],
    queryFn: async () => {
      const { data } = await apiClient.get('/events/list?limit=10');
      return data;
    },
    refetchInterval: 10000, // Refresh every 10s
  });

  // Fetch agent status
  const { data: agentStatus, refetch: refetchAgent } = useQuery<AgentStatus>({
    queryKey: ['agentStatus'],
    queryFn: async () => {
      const { data } = await apiClient.get('/agent/status');
      return data;
    },
    refetchInterval: 5000,
  });

  // Fetch analytics summary
  const { data: analytics } = useQuery<AnalyticsSummary>({
    queryKey: ['analyticsSummary'],
    queryFn: async () => {
      const { data } = await apiClient.get('/analytics/summary');
      return data;
    },
    refetchInterval: 30000,
  });

  const handleRunAgent = async () => {
    try {
      await apiClient.post('/agent/run');
      toast({ title: "Analysis started", description: "AI agent is analyzing your project..." });
      refetchAgent();
    } catch (error) {
      toast({ 
        title: "Failed to run analysis", 
        variant: "destructive",
        description: error instanceof Error ? error.message : "Unknown error"
      });
    }
  };

  const handleLoadDemo = async () => {
    try {
      await apiClient.post('/simulation/run');
      toast({ title: "Demo data loaded", description: "Sample events have been created" });
      window.location.reload();
    } catch (error) {
      toast({ 
        title: "Failed to load demo data", 
        variant: "destructive" 
      });
    }
  };

  const handleToggleAgent = async () => {
    try {
      const endpoint = agentStatus?.is_running ? '/agent/stop' : '/agent/start';
      await apiClient.post(endpoint);
      toast({ 
        title: agentStatus?.is_running ? "Agent stopped" : "Agent started",
        description: agentStatus?.is_running 
          ? "Autonomous monitoring has been paused" 
          : "Autonomous monitoring is now active"
      });
      refetchAgent();
    } catch (error) {
      toast({ title: "Failed to toggle agent", variant: "destructive" });
    }
  };

  const events = eventsData?.events || [];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Project Dashboard</h1>
          <p className="text-muted-foreground mt-1">Real-time intelligence and monitoring</p>
        </div>
        <Button onClick={handleRunAgent} className="gap-2">
          <Sparkles className="h-4 w-4" />
          Run Analysis
        </Button>
      </div>

      {/* Status Hero */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-5">
        <div className="lg:col-span-2">
          <StatusIndicator status={state?.status || 'GREEN'} size="lg" />
        </div>
        <MetricCard
          title="Total Events"
          value={analytics?.total_events || 0}
          icon={Activity}
          trend={analytics?.events_24h_change}
        />
        <MetricCard
          title="Active Blockers"
          value={state?.blockers?.length || 0}
          icon={AlertCircle}
          variant={state?.blockers?.length ? "danger" : "default"}
        />
        <MetricCard
          title="Risk Score"
          value={analytics?.risk_score || 0}
          icon={TrendingUp}
          variant={
            (analytics?.risk_score || 0) > 60 ? "danger" :
            (analytics?.risk_score || 0) > 30 ? "warning" :
            "success"
          }
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Project State */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-card rounded-xl border border-border p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Current Project State</h2>
              {state?.last_updated && (
                <span className="text-sm text-muted-foreground">
                  Updated {formatDistanceToNow(new Date(state.last_updated), { addSuffix: true })}
                </span>
              )}
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              {/* Blockers */}
              <div className="glass-card rounded-lg border border-danger/30 bg-danger/5 p-4">
                <h3 className="text-sm font-semibold text-danger mb-3 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  Blockers
                </h3>
                {state?.blockers && state.blockers.length > 0 ? (
                  <ul className="space-y-2">
                    {state.blockers.map((blocker, i) => (
                      <li key={i} className="text-sm flex items-start gap-2">
                        <span className="text-danger">•</span>
                        <span>{blocker}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-muted-foreground">No blockers detected ✅</p>
                )}
              </div>

              {/* Risks */}
              <div className="glass-card rounded-lg border border-warning/30 bg-warning/5 p-4">
                <h3 className="text-sm font-semibold text-warning mb-3 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  Risks
                </h3>
                {state?.risks && state.risks.length > 0 ? (
                  <ul className="space-y-2">
                    {state.risks.map((risk, i) => (
                      <li key={i} className="text-sm flex items-start gap-2">
                        <span className="text-warning">•</span>
                        <span>{risk}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-muted-foreground">No risks identified 🎯</p>
                )}
              </div>

              {/* Completed */}
              <div className="glass-card rounded-lg border border-success/30 bg-success/5 p-4">
                <h3 className="text-sm font-semibold text-success mb-3 flex items-center gap-2">
                  <Activity className="h-4 w-4" />
                  Completed Today
                </h3>
                {state?.completed_today && state.completed_today.length > 0 ? (
                  <ul className="space-y-2">
                    {state.completed_today.map((item, i) => (
                      <li key={i} className="text-sm flex items-start gap-2">
                        <span className="text-success">•</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-muted-foreground">No items completed yet</p>
                )}
              </div>
            </div>
          </div>

          <EventFeed events={events} />
        </div>

        {/* Right Sidebar */}
        <div className="space-y-6">
          {/* Agent Status */}
          <div className="glass-card rounded-xl border border-border p-6">
            <h3 className="text-lg font-semibold mb-4">Autonomous Agent</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={`h-3 w-3 rounded-full ${agentStatus?.is_running ? 'bg-success animate-pulse-slow' : 'bg-muted'}`} />
                  <span className="text-sm font-medium">
                    {agentStatus?.is_running ? 'Running' : 'Stopped'}
                  </span>
                </div>
                <Button
                  size="sm"
                  variant={agentStatus?.is_running ? "destructive" : "default"}
                  onClick={handleToggleAgent}
                  className="gap-2"
                >
                  {agentStatus?.is_running ? <Pause className="h-3 w-3" /> : <Play className="h-3 w-3" />}
                  {agentStatus?.is_running ? 'Stop' : 'Start'}
                </Button>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Run count:</span>
                  <Badge variant="secondary">{agentStatus?.run_count || 0}</Badge>
                </div>
                {agentStatus?.last_run && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Last run:</span>
                    <span>{formatDistanceToNow(new Date(agentStatus.last_run), { addSuffix: true })}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="glass-card rounded-xl border border-border p-6">
            <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <Button 
                variant="outline" 
                className="w-full justify-start gap-2"
                onClick={handleLoadDemo}
              >
                <Download className="h-4 w-4" />
                Load Demo Data
              </Button>
              <Button 
                variant="outline" 
                className="w-full justify-start gap-2"
                onClick={() => window.location.reload()}
              >
                <RefreshCw className="h-4 w-4" />
                Refresh Dashboard
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
