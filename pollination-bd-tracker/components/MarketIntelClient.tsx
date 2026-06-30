'use client'

import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'
import type { SafeguardRow } from '@/app/market-intelligence/page'

interface Props {
  totalACCUs: number
  totalEmitters: number
  buyerCount: number
  avgIntensity: number
  sectors: { sector: string; volume: number }[]
  topRetirers: SafeguardRow[]
  fetchError: string | null
}

const SECTOR_COLORS = [
  '#10545D', '#276C75', '#499BA6', '#0D4474', '#00579B',
  '#B1DEE5', '#BCDEFF', '#DEEBF7', '#e6e9ef', '#c3c6d4',
]

function fmt(n: number) {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(2) + 'M'
  if (n >= 1_000) return (n / 1_000).toFixed(0) + 'k'
  return n.toLocaleString()
}

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-[#e6e9ef] rounded-lg shadow-lg p-3 text-xs">
      <p className="font-bold text-[#323338] mb-1">{label}</p>
      {payload.map((p: any) => (
        <p key={p.name} style={{ color: p.fill }} className="leading-relaxed">
          {p.name}: <span className="font-semibold">{fmt(p.value)} ACCUs</span>
        </p>
      ))}
    </div>
  )
}

export default function MarketIntelClient({
  totalACCUs, totalEmitters, buyerCount, avgIntensity,
  sectors, topRetirers, fetchError,
}: Props) {
  const STAT_CARDS = [
    {
      label: 'Total ACCUs surrendered',
      value: fmt(totalACCUs),
      sub: 'Safeguard mechanism 2024-25',
      color: '#10545D',
    },
    {
      label: 'Safeguard covered entities',
      value: totalEmitters.toString(),
      sub: 'Responsible emitters 2024-25',
      color: '#276C75',
    },
    {
      label: 'Entities surrendering ACCUs',
      value: buyerCount.toString(),
      sub: `${Math.round((buyerCount / totalEmitters) * 100)}% of covered emitters`,
      color: '#499BA6',
    },
    {
      label: 'Avg ACCU intensity',
      value: avgIntensity + '%',
      sub: 'ACCUs surrendered / covered emissions',
      color: '#0D4474',
    },
  ]

  return (
    <div className="min-h-screen bg-[#f6f7fb]">
      {/* Header */}
      <div className="bg-[#10545D] px-6 py-8">
        <div className="max-w-6xl mx-auto">
          <p className="text-[#B1DEE5] text-xs font-bold uppercase tracking-widest mb-2">
            Pollination · AUS Market Intelligence
          </p>
          <h1 className="text-2xl font-bold text-white mb-1">
            Australian ACCU Market — Safeguard Surrenders
          </h1>
          <p className="text-[#B1DEE5] text-sm">
            CER Safeguard Mechanism 2024-25 · ACCUs surrendered by responsible emitter
            · {fetchError ? <span className="text-red-300">Live data unavailable — {fetchError}</span> : 'Live from CER registry'}
          </p>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8 space-y-8">

        {/* Stat cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {STAT_CARDS.map(s => (
            <div key={s.label} className="bg-white rounded-xl border border-[#e6e9ef] p-5">
              <div className="w-2 h-2 rounded-full mb-3" style={{ background: s.color }} />
              <p className="text-2xl font-bold text-[#323338] leading-none mb-1">{s.value}</p>
              <p className="text-[11px] text-[#676879] font-medium mb-0.5">{s.label}</p>
              <p className="text-[10px] text-[#c3c6d4]">{s.sub}</p>
            </div>
          ))}
        </div>

        {/* Sector breakdown */}
        <div className="bg-white rounded-xl border border-[#e6e9ef] p-6">
          <div className="mb-5">
            <h2 className="text-sm font-bold text-[#323338]">ACCUs Surrendered by Sector</h2>
            <p className="text-xs text-[#676879] mt-0.5">ACCUs — Safeguard 2024-25 (CER data)</p>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={sectors} layout="vertical" barSize={16} margin={{ left: 8, right: 24 }}>
              <XAxis
                type="number"
                tick={{ fontSize: 10, fill: '#676879' }}
                axisLine={false}
                tickLine={false}
                tickFormatter={v => fmt(v)}
              />
              <YAxis
                type="category"
                dataKey="sector"
                tick={{ fontSize: 11, fill: '#676879' }}
                axisLine={false}
                tickLine={false}
                width={100}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="volume" name="ACCUs" radius={[0, 3, 3, 0]}>
                {sectors.map((_, i) => (
                  <Cell key={i} fill={SECTOR_COLORS[i % SECTOR_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Top retirers table */}
        <div className="bg-white rounded-xl border border-[#e6e9ef] overflow-hidden">
          <div className="px-6 py-4 border-b border-[#e6e9ef] flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-[#323338]">Top ACCU Surrenderers</h2>
              <p className="text-xs text-[#676879] mt-0.5">
                By ACCUs surrendered 2024-25 (Safeguard compliance)
              </p>
            </div>
            <span className="text-[10px] bg-[#E2F4F5] text-[#10545D] font-bold px-2 py-1 rounded-full">
              CER Registry
            </span>
          </div>
          <div className="divide-y divide-[#f6f7fb]">
            {topRetirers.map((r, i) => {
              const pct = totalACCUs > 0 ? r.accus_surrendered / topRetirers[0].accus_surrendered : 0
              return (
                <div
                  key={r.company_name}
                  className="grid items-center gap-3 px-6 py-3 hover:bg-[#fafbff] transition-colors"
                  style={{ gridTemplateColumns: '28px 2fr 1fr 120px' }}
                >
                  <span className="text-xs font-bold text-[#c3c6d4]">#{i + 1}</span>
                  <span className="text-sm font-semibold text-[#323338] truncate">{r.company_name}</span>
                  <span className="text-xs text-[#676879]">
                    {r.safeguard_emissions
                      ? `${(r.safeguard_emissions / 1_000_000).toFixed(1)}Mt covered`
                      : '—'}
                  </span>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 rounded-full bg-[#f6f7fb]">
                      <div
                        className="h-full rounded-full bg-[#499BA6]"
                        style={{ width: `${pct * 100}%` }}
                      />
                    </div>
                    <span className="text-xs font-bold text-[#323338] w-14 text-right tabular-nums">
                      {fmt(r.accus_surrendered)}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Data note */}
        <p className="text-[11px] text-[#c3c6d4] text-center pb-4">
          Source: CER Safeguard Mechanism 2024-25 public data, processed via Pollination carbon-intel pipeline.
          ACCU surrenders are compliance-grade (mandatory). Voluntary retirements not included.
        </p>
      </div>
    </div>
  )
}
