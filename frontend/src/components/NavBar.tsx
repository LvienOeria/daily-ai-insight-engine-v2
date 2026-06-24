import { BarChart3, FileText, Gauge, ListTree, ShieldCheck } from "lucide-react";

export type ViewKey = "overview" | "events" | "analysis" | "sources" | "quality";

interface NavBarProps {
  active: ViewKey;
  onChange: (view: ViewKey) => void;
}

const items: Array<{ key: ViewKey; label: string; icon: typeof Gauge }> = [
  { key: "overview", label: "概览", icon: Gauge },
  { key: "events", label: "事件", icon: ListTree },
  { key: "analysis", label: "分析", icon: FileText },
  { key: "sources", label: "数据源", icon: BarChart3 },
  { key: "quality", label: "质量", icon: ShieldCheck },
];

export function NavBar({ active, onChange }: NavBarProps) {
  return (
    <nav className="nav-bar" aria-label="Dashboard views">
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <button
            key={item.key}
            type="button"
            className={active === item.key ? "active" : ""}
            onClick={() => onChange(item.key)}
          >
            <Icon size={16} aria-hidden />
            <span>{item.label}</span>
          </button>
        );
      })}
    </nav>
  );
}

