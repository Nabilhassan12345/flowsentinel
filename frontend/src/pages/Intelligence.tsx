import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Sparkles, Send } from "lucide-react";
import { toast } from "@/hooks/use-toast";

export default function Intelligence() {
  const [question, setQuestion] = useState("");
  const [qaHistory, setQaHistory] = useState<Array<{
    question: string;
    answer: string;
    reasoning?: string[];
    timestamp: string;
  }>>([]);

  const askMutation = useMutation({
    mutationFn: async (q: string) => {
      const { data } = await apiClient.post('/qa/ask', { question: q });
      return data;
    },
    onSuccess: (data) => {
      setQaHistory(prev => [{
        question,
        answer: data.answer,
        reasoning: data.reasoning_steps,
        timestamp: new Date().toISOString()
      }, ...prev]);
      setQuestion("");
      toast({ title: "Answer received", description: "AI has analyzed your question" });
    },
    onError: () => {
      toast({ title: "Failed to get answer", variant: "destructive" });
    }
  });

  const { data: deadlineRisk } = useQuery({
    queryKey: ['deadlineRisk'],
    queryFn: async () => {
      const { data } = await apiClient.get('/intelligence/predict-deadline-risk');
      return data;
    },
  });

  const { data: bottlenecks } = useQuery({
    queryKey: ['bottlenecks'],
    queryFn: async () => {
      const { data } = await apiClient.get('/intelligence/predict-bottlenecks');
      return data;
    },
  });

  const { data: teamHealth } = useQuery({
    queryKey: ['teamHealth'],
    queryFn: async () => {
      const { data } = await apiClient.get('/intelligence/team-health');
      return data;
    },
  });

  const prefilledQuestions = [
    "What's blocking the team?",
    "Is the project at risk?",
    "What's the overall status?",
    "Why might we miss the deadline?"
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold">AI-Powered Intelligence</h1>
        <p className="text-muted-foreground mt-1">IBM watsonx.ai Granite 3 8B Instruct</p>
      </div>

      {/* Q&A Section */}
      <Card className="glass-card p-6">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-accent" />
          Ask Anything
        </h2>
        
        <div className="space-y-4">
          <div className="flex gap-2">
            <Input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask anything about your project..."
              className="flex-1"
              onKeyPress={(e) => e.key === 'Enter' && question && askMutation.mutate(question)}
            />
            <Button 
              onClick={() => question && askMutation.mutate(question)}
              disabled={!question || askMutation.isPending}
              className="gap-2"
            >
              <Send className="h-4 w-4" />
              Ask
            </Button>
          </div>

          <div className="flex flex-wrap gap-2">
            {prefilledQuestions.map((q) => (
              <Button
                key={q}
                variant="outline"
                size="sm"
                onClick={() => setQuestion(q)}
              >
                {q}
              </Button>
            ))}
          </div>

          {/* Q&A History */}
          <div className="space-y-4 mt-6">
            {qaHistory.map((qa, i) => (
              <Card key={i} className="p-4 border-primary/20">
                <p className="font-semibold mb-2">{qa.question}</p>
                <p className="text-muted-foreground mb-2">{qa.answer}</p>
                {qa.reasoning && qa.reasoning.length > 0 && (
                  <details className="text-sm text-muted-foreground mt-2">
                    <summary className="cursor-pointer">Reasoning steps</summary>
                    <ul className="list-disc list-inside mt-2 space-y-1">
                      {qa.reasoning.map((step, j) => (
                        <li key={j}>{step}</li>
                      ))}
                    </ul>
                  </details>
                )}
              </Card>
            ))}
          </div>
        </div>
      </Card>

      {/* Predictions */}
      <div className="grid gap-6 md:grid-cols-3">
        {/* Deadline Risk */}
        <Card className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Deadline Risk</h3>
          {deadlineRisk && (
            <div className="space-y-4">
              <div>
                <div className="flex items-baseline gap-2 mb-2">
                  <span className="text-3xl font-bold text-danger">
                    {Math.round((deadlineRisk.risk_percentage || 0) * 100)}%
                  </span>
                  <span className="text-sm text-muted-foreground">Risk</span>
                </div>
                <Progress value={(deadlineRisk.risk_percentage || 0) * 100} className="h-2" />
              </div>
              {deadlineRisk.contributing_factors && (
                <div>
                  <p className="text-sm font-medium mb-2">Contributing Factors:</p>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    {deadlineRisk.contributing_factors.map((factor: string, i: number) => (
                      <li key={i}>• {factor}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </Card>

        {/* Bottlenecks */}
        <Card className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Bottleneck Detection</h3>
          {bottlenecks?.bottlenecks && bottlenecks.bottlenecks.length > 0 ? (
            <div className="space-y-3">
              {bottlenecks.bottlenecks.map((b: any, i: number) => (
                <div key={i} className="border-l-2 border-warning pl-3">
                  <p className="font-medium text-sm">{b.area}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="outline" className="text-xs">
                      {Math.round(b.probability * 100)}% likely
                    </Badge>
                    <span className="text-xs text-muted-foreground">{b.impact} impact</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No bottlenecks detected</p>
          )}
        </Card>

        {/* Team Health */}
        <Card className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Team Health</h3>
          {teamHealth && (
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-4xl font-bold mb-2">
                  {teamHealth.health_score || 0}
                  <span className="text-lg text-muted-foreground">/100</span>
                </div>
                <Badge variant={
                  (teamHealth.health_score || 0) >= 80 ? "default" :
                  (teamHealth.health_score || 0) >= 60 ? "secondary" :
                  "destructive"
                }>
                  Grade {teamHealth.grade || 'N/A'}
                </Badge>
              </div>
              {teamHealth.status && (
                <p className="text-sm text-center text-muted-foreground">
                  {teamHealth.status}
                </p>
              )}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
