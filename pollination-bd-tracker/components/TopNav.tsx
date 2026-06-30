'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, Flame, Building2, Kanban, BarChart2 } from 'lucide-react'

const NAV = [
  { href: '/', label: 'Home', icon: Home, exact: true },
  { href: '/hot-sheet', label: 'Hot Sheet', icon: Flame },
  { href: '/companies', label: 'Companies', icon: Building2 },
  { href: '/pipeline', label: 'Pipeline', icon: Kanban },
  { href: '/market-intelligence', label: 'AUS Market Intelligence', icon: BarChart2 },
]

export default function TopNav() {
  const pathname = usePathname()

  return (
    <header className="h-14 bg-white border-b border-[#e6e9ef] flex items-center px-5 gap-6 sticky top-0 z-20 shadow-[0_2px_4px_rgba(0,0,0,0.04)]">
      {/* Logo */}
      <Link href="/" className="flex items-center gap-2 shrink-0 group">
        <div className="w-7 h-7 rounded-lg bg-[#10545D] flex items-center justify-center">
          <div className="w-2.5 h-2.5 rounded-full bg-[#B1DEE5]" />
        </div>
        <span className="font-bold text-[#323338] text-sm hidden sm:block group-hover:text-[#10545D] transition-colors">
          Pollination <span className="font-normal text-[#676879]">BD</span>
        </span>
      </Link>

      {/* Divider */}
      <div className="h-6 w-px bg-[#e6e9ef]" />

      {/* Nav links */}
      <nav className="flex items-center gap-0.5 overflow-x-auto">
        {NAV.map(({ href, label, icon: Icon, exact }) => {
          const active = exact ? pathname === href : pathname.startsWith(href)
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-sm font-medium transition-all whitespace-nowrap ${
                active
                  ? 'text-[#10545D] bg-[#E2F4F5]'
                  : 'text-[#676879] hover:text-[#323338] hover:bg-[#f6f7fb]'
              }`}
            >
              <Icon size={15} strokeWidth={active ? 2.5 : 2} />
              <span className="hidden md:block">{label}</span>
            </Link>
          )
        })}
      </nav>
    </header>
  )
}
