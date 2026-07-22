interface VintageCardProps {
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
}

export function VintageCard({ children, onClick, className = '' }: VintageCardProps) {
  return (
    <div
      onClick={onClick}
      className={`vintage-card rounded-sm p-4 transition-all duration-200 ${
        onClick ? 'cursor-pointer' : ''
      } ${className}`}
    >
      {children}
    </div>
  );
}
