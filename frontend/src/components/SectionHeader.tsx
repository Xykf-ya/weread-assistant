interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  count?: number;
  className?: string;
  titleClassName?: string;
}

export function SectionHeader({ title, subtitle, icon, count, className = '', titleClassName = '' }: SectionHeaderProps) {
  return (
    <div className={`flex items-center gap-3 mb-4 px-1 ${className}`}>
      <div className="flex-shrink-0">
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <h2 className={`font-display text-xl font-bold text-sepia-800 tracking-wide ${titleClassName}`}>{title}</h2>
        {subtitle && <p className="text-sm text-sepia-500 font-handwriting">{subtitle}</p>}
      </div>
      {count !== undefined && (
        <span className="date-badge">{count}</span>
      )}
    </div>
  );
}
