import { LucideIcon, TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: number;
  suffix?: string;
  variant?: "default" | "success" | "warning" | "danger";
}

export function MetricCard({ 
  title, 
  value, 
  icon: Icon, 
  trend,
  suffix,
  variant = "default" 
}: MetricCardProps) {
  const variantStyles = {
    default: "border-border",
    success: "border-success/30 bg-success/5",
    warning: "border-warning/30 bg-warning/5",
    danger: "border-danger/30 bg-danger/5",
  };

  return (
    <div className={cn(
      "glass-card rounded-xl border p-6 transition-all hover:shadow-lg hover:scale-[1.02]",
      variantStyles[variant]
    )}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-muted-foreground mb-1">{title}</p>
          <p className="text-3xl font-bold">
            {value}
            {suffix && <span className="text-lg text-muted-foreground ml-1">{suffix}</span>}
          </p>
          {trend !== undefined && (
            <div className={cn(
              "flex items-center gap-1 mt-2 text-sm font-medium",
              trend > 0 ? "text-success" : trend < 0 ? "text-danger" : "text-muted-foreground"
            )}>
              {trend > 0 ? (
                <TrendingUp className="h-4 w-4" />
              ) : trend < 0 ? (
                <TrendingDown className="h-4 w-4" />
              ) : null}
              <span>{Math.abs(trend)}%</span>
              <span className="text-muted-foreground">vs 24h</span>
            </div>
          )}
        </div>
        <div className={cn(
          "rounded-lg p-3",
          variant === "success" ? "bg-success/10" :
          variant === "warning" ? "bg-warning/10" :
          variant === "danger" ? "bg-danger/10" :
          "bg-primary/10"
        )}>
          <Icon className={cn(
            "h-6 w-6",
            variant === "success" ? "text-success" :
            variant === "warning" ? "text-warning" :
            variant === "danger" ? "text-danger" :
            "text-primary"
          )} />
        </div>
      </div>
    </div>
  );
}
