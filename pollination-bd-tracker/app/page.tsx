import Link from 'next/link'
import { Flame, Building2, Kanban, BarChart2, ArrowRight, TrendingUp, Target, Users } from 'lucide-react'

const CARDS = [
  {
    href: '/hot-sheet',
    icon: Flame,
    label: 'Hot Sheet',
    description: '10 priority prospects with carbon market DD, news, and contact intelligence.',
    color: '#499BA6',
    bg: '#E2F4F5',
  },
  {
    href: '/companies',
    icon: Building2,
    label: 'Company Database',
    description: 'Full universe of Australian companies — filter by ASRS group, SBTi status, NGER, sector.',
    color: '#276C75',
    bg: '#E2F4F5',
  },
  {
    href: '/pipeline',
    icon: Kanban,
    label: 'Pipeline',
    description: 'Kanban view of active prospects with stage tracking and key contacts.',
    color: '#0073ea',
    bg: '#E4F1FF',
  },
  {
    href: '/market-intelligence',
    icon: BarChart2,
    label: 'AUS Market Intelligence',
    description: 'NGER retirement data — who is buying what credits, volumes, and sector trends.',
    color: '#10545D',
    bg: '#E2F4F5',
  },
]

const STATS = [
  { label: 'Companies tracked', value: '1,000+', icon: Building2 },
  { label: 'Priority prospects', value: '10', icon: Target },
  { label: 'Group 1 reporters', value: '~100', icon: TrendingUp },
  { label: 'SBTi committed (AU)', value: '112', icon: Users },
]

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[#f6f7fb]">
      {/* Hero */}
      <div className="bg-[#10545D] px-8 py-16">
        <div className="max-w-4xl mx-auto">
          {/* Pollination wordmark */}
          <div className="flex items-center gap-3 mb-10">
            <div className="w-8 h-8 rounded bg-[#499BA6]/30 flex items-center justify-center">
              <div className="w-3 h-3 rounded-full bg-[#B1DEE5]" />
            </div>
            <span className="text-[#B1DEE5] text-sm font-semibold tracking-widest uppercase">Pollination</span>
          </div>

          <h1 className="text-4xl font-bold text-white leading-tight mb-4">
            Australian Business<br />Development Intelligence
          </h1>
          <p className="text-[#B1DEE5] text-lg leading-relaxed max-w-2xl">
            Climate-disclosure mandates, SBTi commitments, and carbon market activity —
            prioritised into a single pipeline for the Australian BD team.
          </p>

          <div className="mt-8 flex items-center gap-4">
            <Link
              href="/hot-sheet"
              className="inline-flex items-center gap-2 bg-[#499BA6] hover:bg-[#276C75] text-white font-semibold px-5 py-2.5 rounded-lg transition-colors text-sm"
            >
              View Hot Sheet <ArrowRight size={15} />
            </Link>
            <Link
              href="/market-intelligence"
              className="inline-flex items-center gap-2 text-[#B1DEE5] hover:text-white font-medium text-sm transition-colors"
            >
              AUS Market Intelligence <ArrowRight size={14} />
            </Link>
          </div>
        </div>
      </div>

      {/* Stats bar */}
      <div className="bg-[#0D4474] px-8 py-5">
        <div className="max-w-4xl mx-auto grid grid-cols-2 sm:grid-cols-4 gap-6">
          {STATS.map(({ label, value, icon: Icon }) => (
            <div key={label} className="flex items-center gap-3">
              <Icon size={16} className="text-[#BCDEFF] shrink-0" />
              <div>
                <p className="text-white font-bold text-lg leading-none">{value}</p>
                <p className="text-[#BCDEFF] text-xs mt-0.5">{label}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Cards */}
      <div className="max-w-4xl mx-auto px-8 py-12">
        <p className="text-xs font-bold text-[#676879] uppercase tracking-widest mb-6">Explore the data</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {CARDS.map(({ href, icon: Icon, label, description, color, bg }) => (
            <Link
              key={href}
              href={href}
              className="group bg-white rounded-xl border border-[#e6e9ef] p-6 hover:border-[#499BA6]/40 hover:shadow-lg transition-all"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: bg }}>
                  <Icon size={18} style={{ color }} />
                </div>
                <ArrowRight size={16} className="text-[#c3c6d4] group-hover:text-[#499BA6] transition-colors mt-1" />
              </div>
              <h2 className="text-sm font-bold text-[#323338] mb-1.5">{label}</h2>
              <p className="text-xs text-[#676879] leading-relaxed">{description}</p>
            </Link>
          ))}
        </div>

        {/* Context note */}
        <div className="mt-8 p-5 bg-white rounded-xl border border-[#e6e9ef]">
          <div className="flex items-start gap-4">
            <div className="w-1 self-stretch rounded-full bg-[#499BA6] shrink-0" />
            <div>
              <p className="text-xs font-bold text-[#323338] mb-1">ASRS Mandatory Disclosure — Coming Now</p>
              <p className="text-xs text-[#676879] leading-relaxed">
                Group 1 entities (revenue &gt;$500M or assets &gt;$1B or employees &gt;500) must report from FY2025/26.
                Group 2 from FY2026/27. Group 3 from FY2027/28. Companies without credible transition plans
                face increasing investor and regulatory scrutiny — the BD window is now.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
