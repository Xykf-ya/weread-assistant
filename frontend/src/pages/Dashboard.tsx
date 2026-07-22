import { Header } from '../components/Header';
import { OpportunitySection } from '../components/OpportunitySection';
import { CampusSection } from '../components/CampusSection';
import { NewsSection } from '../components/NewsSection';
import { InterestSection } from '../components/InterestSection';

interface DashboardProps {
  onSyncStart?: () => void;
  onSyncEnd?: (result: any) => void;
}

export function Dashboard({ onSyncStart, onSyncEnd }: DashboardProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <Header onSyncStart={onSyncStart} onSyncEnd={onSyncEnd} />
      
      <main className="flex-1 p-4 md:p-6">
        <div className="max-w-7xl mx-auto">
          {/* Date Header */}
          <div className="text-center mb-8">
            <p className="font-handwriting text-sepia-500 text-xl">
              {new Date().toLocaleDateString('zh-CN', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </p>
            <div className="newspaper-line w-full max-w-md mx-auto mt-3" />
          </div>

          {/* Main Content - Four Vertical Columns */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-0">
            {/* Column 1: Opportunities */}
            <div className="relative p-4 md:p-6 border-r border-sepia-300 border-dashed">
              <div className="sticky top-4">
                <OpportunitySection />
              </div>
            </div>

            {/* Column 2: Campus */}
            <div className="relative p-4 md:p-6 border-r border-sepia-300 border-dashed">
              <CampusSection />
            </div>

            {/* Column 3: News */}
            <div className="relative p-4 md:p-6 border-r border-sepia-300 border-dashed">
              <div className="sticky top-4">
                <NewsSection />
              </div>
            </div>

            {/* Column 4: Interest */}
            <div className="relative p-4 md:p-6">
              <InterestSection />
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="vintage-footer text-parchment-400 py-4 px-6 mt-8">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-2">
          <p className="text-sm font-handwriting">
            WeRead — 你的专属公众号摘要
          </p>
          <p className="text-xs text-parchment-500">
            基于 WeRSS & AI 技术驱动
          </p>
        </div>
      </footer>
    </div>
  );
}
