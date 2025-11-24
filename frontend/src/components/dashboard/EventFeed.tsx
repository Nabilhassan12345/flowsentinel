import { MessageSquare, GitBranch, Calendar as CalendarIcon, FileText, Calendar } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { Event } from "@/lib/api";

const sourceIcons = {
  slack: MessageSquare,
  github: GitBranch,
  calendar: CalendarIcon,
  jira: FileText,
};

const sourceColors = {
  slack: "text-purple-400",
  github: "text-orange-400",
  calendar: "text-blue-400",
  jira: "text-cyan-400",
};

interface EventFeedProps {
  events: Event[];
}

export function EventFeed({ events }: EventFeedProps) {
  return (
    <div className="glass-card rounded-xl border border-border p-6">
      <h3 className="text-lg font-semibold mb-4">Real-Time Activity</h3>
      <ScrollArea className="h-[400px] pr-4">
        <div className="space-y-4">
          {events.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="rounded-full bg-muted p-4 mb-4">
                <Calendar className="h-8 w-8 text-muted-foreground" />
              </div>
              <p className="text-muted-foreground">No events yet</p>
              <p className="text-sm text-muted-foreground mt-1">Events will appear here as they happen</p>
            </div>
          ) : (
            events.map((event) => {
              const Icon = sourceIcons[event.source];
              const iconColor = sourceColors[event.source];
              
              return (
                <div 
                  key={event.id}
                  className="flex gap-3 rounded-lg border border-border/50 bg-card/50 p-4 transition-all hover:bg-card/80"
                >
                  <div className={`rounded-lg bg-background p-2 ${iconColor}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge variant="outline" className="text-xs capitalize">
                        {event.source}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
                      </span>
                    </div>
                    <p className="text-sm font-medium truncate">{event.type}</p>
                    {event.data?.message && (
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                        {event.data.message}
                      </p>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
