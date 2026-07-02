'use client'

import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'
import type { SafeguardRow } from '@/app/market-intelligence/page'

interface StrategyMixItem {
  strategy: string
  count: number
  accus: number
  smcs: number
}

interface Props {
  totalACCUs: number
  totalEmitters: number
  buyerCount: number
  avgIntensity: number
  sectors: { sector: string; volume: number }[]
  methodBreakdown: { method: string; volume: number }[]
  topRetirers: SafeguardRow[]
  fetchError: string | null
  totalSMCs: number
  strategyMix: StrategyMixItem[]
  smcOnlyEntities: SafeguardRow[]
}

const SECTOR_COLORS = [
  '#10545D', '#276C75', '#499BA6', '#0D4474', '#00579B',
  '#B1DEE5', '#BCDEFF', '#DEEBF7', '#e6e9ef', '#c3c6d4',
]

// Consistent colour per method type
const METHOD_COLOR: Record<string, string> = {
  'Vegetation':              '#276C75',
  'Waste':                   '#499BA6',
  'Savanna Fire Management': '#e86f2c',
  'Industrial Fugitives':    '#0D4474',
  'Facilities':              '#00579B',
  'Energy Efficiency':       '#00c875',
  'Agriculture':             '#8bc34a',
  'Carbon Capture':          '#a25ddc',
  'Transport':               '#fdab3d',
}
const METHOD_BG: Record<string, string> = {
  'Vegetation':              '#E2F4F5',
  'Waste':                   '#dff0f5',
  'Savanna Fire Management': '#fde8d8',
  'Industrial Fugitives':    '#dce8f5',
  'Facilities':              '#cce5ff',
  'Energy Efficiency':       '#d4f4e2',
  'Agriculture':             '#eaf3d8',
  'Carbon Capture':          '#ede0f7',
  'Transport':               '#fff3cd',
}

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

function MethodPills({ byMethod }: { byMethod: Record<string, number> | null }) {
  if (!byMethod) return <span className="text-[#c3c6d4] text-[10px]">—</span>
  const sorted = Object.entries(byMethod).sort((a, b) => b[1] - a[1])
  return (
    <div className="flex flex-wrap gap-1">
      {sorted.map(([method, qty]) => (
        <span
          key={method}
          className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold leading-none"
          style={{
            background: METHOD_BG[method] ?? '#f6f7fb',
            color: METHOD_COLOR[method] ?? '#676879',
          }}
          title={`${method}: ${qty.toLocaleString()} ACCUs`}
        >
          {method === 'Savanna Fire Management' ? 'Savanna' : method}
          <span className="opacity-70">{fmt(qty)}</span>
        </span>
      ))}
    </div>
  )
}

export default function MarketIntelClient({
  totalACCUs, totalEmitters, buyerCount, avgIntensity,
  sectors, methodBreakdown, topRetirers, fetchError,
  totalSMCs, strategyMix, smcOnlyEntities,
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
    {
      label: 'SMCs surrendered',
      value: fmt(totalSMCs),
      sub: 'Safeguard Mechanism Credits 2024-25',
      color: '#e86f2c',
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
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
          {STAT_CARDS.map(s => (
            <div key={s.label} className="bg-white rounded-xl border border-[#e6e9ef] p-5">
              <div className="w-2 h-2 rounded-full mb-3" style={{ background: s.color }} />
              <p className="text-2xl font-bold text-[#323338] leading-none mb-1">{s.value}</p>
              <p className="text-[11px] text-[#676879] font-medium mb-0.5">{s.label}</p>
              <p className="text-[10px] text-[#c3c6d4]">{s.sub}</p>
            </div>
          ))}
        </div>

        {/* Two-column: sector + method type */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Sector breakdown */}
          <div className="bg-white rounded-xl border border-[#e6e9ef] p-6">
            <div className="mb-5">
              <h2 className="text-sm font-bold text-[#323338]">ACCUs Surrendered by Sector</h2>
              <p className="text-xs text-[#676879] mt-0.5">Safeguard 2024-25</p>
            </div>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={sectors} layout="vertical" barSize={14} margin={{ left: 8, right: 24 }}>
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

          {/* Method type breakdown */}
          <div className="bg-white rounded-xl border border-[#e6e9ef] p-6">
            <div className="mb-5">
              <h2 className="text-sm font-bold text-[#323338]">2024-25 Surrenders by ACCU Method</h2>
              <p className="text-xs text-[#676879] mt-0.5">All Safeguard entities · project methodology category</p>
            </div>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={methodBreakdown} layout="vertical" barSize={14} margin={{ left: 8, right: 24 }}>
                <XAxis
                  type="number"
                  tick={{ fontSize: 10, fill: '#676879' }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={v => fmt(v)}
                />
                <YAxis
                  type="category"
                  dataKey="method"
                  tick={{ fontSize: 11, fill: '#676879' }}
                  axisLine={false}
                  tickLine={false}
                  width={130}
                  tickFormatter={(v: string) => v === 'Savanna Fire Management' ? 'Savanna Fire' : v}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="volume" name="ACCUs" radius={[0, 3, 3, 0]}>
                  {methodBreakdown.map(({ method }) => (
                    <Cell key={method} fill={METHOD_COLOR[method] ?? '#c3c6d4'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Compliance Strategy Mix */}
        <div className="bg-white rounded-xl border border-[#e6e9ef] p-6">
          <div className="mb-5">
            <h2 className="text-sm font-bold text-[#323338]">Compliance Strategy Mix</h2>
            <p className="text-xs text-[#676879] mt-0.5">
              How 177 obligated entities met their 2024-25 obligations
            </p>
          </div>
          {/* Segmented bar */}
          {(() => {
            const totalCount = strategyMix.reduce((s, x) => s + x.count, 0)
            const STRATEGY_META: Record<string, { label: string; color: string }> = {
              accu:  { label: 'ACCU buyers',    color: '#276C75' },
              mixed: { label: 'ACCU + SMC',     color: '#499BA6' },
              smc:   { label: 'SMC only',        color: '#e86f2c' },
              none:  { label: 'No surrenders',   color: '#c3c6d4' },
            }
            return (
              <>
                <div className="flex w-full h-8 rounded-lg overflow-hidden mb-4">
                  {strategyMix.map(x => {
                    const pct = totalCount > 0 ? (x.count / totalCount) * 100 : 0
                    const meta = STRATEGY_META[x.strategy] ?? { label: x.strategy, color: '#c3c6d4' }
                    return (
                      <div
                        key={x.strategy}
                        style={{ width: `${pct}%`, background: meta.color }}
                        title={`${meta.label}: ${x.count} entities`}
                      />
                    )
                  })}
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {strategyMix.map(x => {
                    const meta = STRATEGY_META[x.strategy] ?? { label: x.strategy, color: '#c3c6d4' }
                    return (
                      <div key={x.strategy} className="flex flex-col gap-1">
                        <div className="flex items-center gap-1.5">
                          <div className="w-2.5 h-2.5 rounded-sm flex-shrink-0" style={{ background: meta.color }} />
                          <span className="text-xs font-semibold text-[#323338]">{meta.label}</span>
                        </div>
                        <p className="text-xl font-bold text-[#323338] leading-none">{x.count}</p>
                        <p className="text-[10px] text-[#676879]">entities</p>
                        {x.accus > 0 && (
                          <p className="text-[10px] text-[#499BA6] font-medium">{fmt(x.accus)} ACCUs</p>
                        )}
                        {x.smcs > 0 && (
                          <p className="text-[10px] text-[#e86f2c] font-medium">{fmt(x.smcs)} SMCs</p>
                        )}
                      </div>
                    )
                  })}
                </div>
              </>
            )
          })()}
        </div>

        {/* SMC-Only Prospects table */}
        <div className="bg-white rounded-xl border border-[#e6e9ef] overflow-hidden">
          <div className="px-6 py-4 border-b border-[#e6e9ef] flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-[#323338]">SMC-Only Compliers — Greenfield ACCU Prospects</h2>
              <p className="text-xs text-[#676879] mt-0.5">
                Obligated entities with no established ACCU procurement — no incumbent carbon-credit strategy
              </p>
            </div>
            <span className="text-[10px] bg-[#fde8d8] text-[#e86f2c] font-bold px-2 py-1 rounded-full">
              BD Prospects
            </span>
          </div>
          <div className="divide-y divide-[#f6f7fb]">
            {smcOnlyEntities.map((r, i) => (
              <div key={r.company_name} className="px-6 py-3 hover:bg-[#fafbff] transition-colors">
                <div
                  className="grid items-center gap-3"
                  style={{ gridTemplateColumns: '28px 2fr 1fr 1fr' }}
                >
                  <span className="text-xs font-bold text-[#c3c6d4]">#{i + 1}</span>
                  <span className="text-sm font-semibold text-[#323338] truncate">{r.company_name}</span>
                  <span className="text-xs text-[#676879]">
                    {r.net_emissions != null
                      ? r.net_emissions >= 1_000_000
                        ? `${(r.net_emissions / 1_000_000).toFixed(1)}Mt net`
                        : `${Math.round(r.net_emissions / 1_000)}k net`
                      : '—'}
                  </span>
                  <span className="text-xs font-bold text-[#e86f2c] text-right tabular-nums">
                    {r.smcs_surrendered != null && r.smcs_surrendered > 0 ? fmt(r.smcs_surrendered) + ' SMCs' : '—'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top retirers table with method pills */}
        <div className="bg-white rounded-xl border border-[#e6e9ef] overflow-hidden">
          <div className="px-6 py-4 border-b border-[#e6e9ef] flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-[#323338]">Top ACCU Surrenderers</h2>
              <p className="text-xs text-[#676879] mt-0.5">
                By ACCUs surrendered 2024-25 · method type pills show project category mix
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
                <div key={r.company_name} className="px-6 py-3 hover:bg-[#fafbff] transition-colors">
                  <div
                    className="grid items-center gap-3 mb-2"
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
                  <div className="ml-7">
                    <MethodPills byMethod={r.surrendered_by_method} />
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Data note */}
        <p className="text-[11px] text-[#c3c6d4] text-center pb-4">
          Source: CER Safeguard Mechanism 2024-25 public data. ACCU and SMC surrender data included.
          Method type from ACCU methodology determination. Annual trend requires prior-year CER surrender CSVs (not yet ingested).
        </p>
      </div>
    </div>
  )
}
