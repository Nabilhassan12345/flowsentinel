import { CheckCircle, AlertTriangle, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { StatusType } from "@/lib/api";

interface StatusIndicatorProps {
  status: StatusType;
  size?: "sm" | "md" | "lg";
}

export function StatusIndicator({ status, size = "md" }: StatusIndicatorProps) {
  const sizeClasses = {
    sm: "text-sm",
    md: "text-base",
    lg: "text-2xl",
  };

  const iconSizes = {
    sm: "h-4 w-4",
    md: "h-6 w-6",
    lg: "h-12 w-12",
  };

  const config = {
    GREEN: {
      icon: CheckCircle,
      label: "Healthy",
      color: "text-success",
      bgColor: "bg-success/10",
      borderColor: "border-success/30",
      dotColor: "bg-success",
    },
    YELLOW: {
      icon: AlertTriangle,
      label: "At Risk",
      color: "text-warning",
      bgColor: "bg-warning/10",
      borderColor: "border-warning/30",
      dotColor: "bg-warning",
    },
    RED: {
      icon: AlertCircle,
      label: "Critical",
      color: "text-danger",
      bgColor: "bg-danger/10",
      borderColor: "border-danger/30",
      dotColor: "bg-danger",
    },
  };

  const { icon: Icon, label, color, bgColor, borderColor, dotColor } = config[status];

  return (
    <div className={cn(
      "glass-card flex items-center gap-4 rounded-xl border-2 p-6",
      borderColor,
      bgColor
    )}>
      <div className="relative">
        <Icon className={cn(iconSizes[size], color)} />
        <div className={cn(
          "absolute -right-1 -top-1 h-3 w-3 rounded-full animate-pulse-slow",
          dotColor
        )} />
      </div>
      <div>
        <p className="text-sm text-muted-foreground">Project Status</p>
        <p className={cn("font-bold", sizeClasses[size], color)}>{label}</p>
      </div>
    </div>
  );
}
