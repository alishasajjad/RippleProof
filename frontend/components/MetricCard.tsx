import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  label: string;
  value: string | number;
  hint: string;
  icon: LucideIcon;
  tone?: 'neutral' | 'good' | 'warn' | 'danger';
}

export default function MetricCard({ label, value, hint, icon: Icon, tone = 'neutral' }: MetricCardProps) {
  return (
    <div className={`metric-card tone-${tone}`}>
      <div className="metric-icon"><Icon size={18} /></div>
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      <div className="metric-hint">{hint}</div>
    </div>
  );
}
