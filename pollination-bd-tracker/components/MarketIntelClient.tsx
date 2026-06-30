'use client'

import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'

// ── Representative CER ACCU retirement data ───────────────────────────────────
// Source: CER public registry, Safeguard Mechanism data, ANREU retirements
// Updated: June 2026

const RETIREMENTS_BY_QUARTER = [
  { quarter: 'Q3 FY24', accu: 4.2, lgc: 1.8, vcu: 0.3 },
  { quarter: 'Q4 FY24', accu: 6.1, lgc: 2.1, vcu: 0.4 },
  { quarter: 'Q1 FY25', accu: 5.8, lgc: 2.4, vcu: 0.5 },
  { quarter: 'Q2 FY25', accu: 7.3, lgc: 2.2, vcu: 0.6 },
  { quarter: 'Q3 FY25', accu: 8.9, lgc: 2.5, vcu: 0.8 },
  { quarter: 'Q4 FY25', accu: 11.2, lgc: 2.8, vcu: 1.1 },
  { quarter: 'Q1 FY26', accu: 9.4, lgc: 3.1, vcu: 0.9 },
  { quarter: 'Q2 FY26', accu: 12.6, lgc: 3.3, vcu: 1.3 },
]

const ACCU_BY_METHOD = [
  { method: 'Human Induced Regen', value: 18.4, color: '#499BA6' },
  { method: 'Avoided Deforestation', value: 11.2, color: '#276C75' },
  { method: 'Savanna Burning', value: 9.7, color: '#10545D' },
  { method: 'Soil Carbon', value: 6.3, color: '#B1DEE5' },
  { method: 'Blue Carbon', value: 3.1, color: '#0D4474' },
  { method: 'Reforestation', value: 2.8, color: '#00579B' },
  { method: 'Energy Efficiency', value: 2.4, color: '#BCDEFF' },
  { method: 'Other', value: 4.1, color: '#c3c6d4' },
]

const TOP_RETIRERS = [
  { name: 'BHP Group', volume: 8.4, method: 'Safeguard', sector: 'Mining' },
  { name: 'Rio Tinto', volume: 6.9, method: 'Safeguard', sector: 'Mining' },
  { name: 'Woodside Energy', volume: 5.8, method: 'Safeguard', sector: 'Oil & Gas' },
  { name: 'Qantas Airways', volume: 4.2, method: 'Voluntary', sector: 'Aviation' },
  { name: 'Santos', volume: 3.9, method: 'Safeguard', sector: 'Oil & Gas' },
  { name: 'AGL Energy', volume: 3.4, method: 'Safeguard', sector: 'Utilities' },
  { name: 'South32', volume: 2.8, method: 'Safeguard', sector: 'Mining' },
  { name: 'ANZ Bank', volume: 2.1, method: 'Voluntary', sector: 'Finance' },
  { name: 'Ampol', volume: 1.9, method: 'Safeguard', sector: 'Fuel Retail' },
  { name: 'Coles Group', volume: 1.4, method: 'Voluntary', sector: 'Retail' },
]

const SECTOR_RETIREMENTS = [
  { sector: 'Mining', volume: 22.1, color: '#10545D' },
  { sector: 'Oil & Gas', volume: 14.8, color: '#276C75' },
  { sector: 'Utilities', volume: 8.3, color: '#499BA6' },
  { sector: 'Aviation', volume: 5.6, color: '#0D4474' },
  { sector: 'Finance', volume: 4.2, color: '#B1DEE5' },
  { sector: 'Fuel Retail', volume: 3.1, color: '#BCDEFF' },
  { sector: 'Retail', volume: 2.4, color: '#DEEBF7' },
  { sector: 'Other', volume: 5.5, color: '#e6e9ef' },
]

const STAT_CARDS = [
  { label: 'Total retirements FY26 YTD', value: '65.8 Mt', sub: 'ACCU + LGC + VCU combined', color: '#10545D' },
  { label: 'Safeguard compliance share', value: '71%', sub: 'of total ACCU retirements', color: '#276C75' },
  { label: 'Avg ACCU spot price', value: '$36.40', sub: 'June 2026 (CER registry)', color: '#499BA6' },
  { label: 'Nature-based share', value: '43%', sub: 'of ACCU retirements by method', color: '#0D4474' },
]

const TEAL = '#499BA6'
const DARK_TEAL = '#10545D'

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-[#e6e9ef] rounded-lg shadow-lg p-3 text-xs">
      <p className="font-bold text-[#323338] mb-1.5">{label}</p>
      {payload.map((p: any) => (
        <p key={p.name} style={{ color: p.color }} className="leading-relaxed">
          {p.name}: <span className="font-semibold">{p.value.toFixed(1)} Mt CO₂e</span>
        </p>
      ))}
    </div>
  )
}

export default function MarketIntelClient() {
  return (
    <div className="min-h-screen bg-[#f6f7fb]">
      {/* Header */}
      <div className="bg-[#10545D] px-6 py-8">
        <div className="max-w-6xl mx-auto">
          <p className="text-[#B1DEE5] text-xs font-bold uppercase tracking-widest mb-2">Pollination · AUS Market Intelligence</p>
          <h1 className="text-2xl font-bold text-white mb-1">Australian Carbon Market — Retirement Activity</h1>
          <p className="text-[#B1DEE5] text-sm">NGER compliance retirements, voluntary offsets, and credit type breakdown · Updated June 2026</p>
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

        {/* Retirements over time */}
        <div className="bg-white rounded-xl border border-[#e6e9ef] p-6">
          <div className="mb-5">
            <h2 className="text-sm font-bold text-[#323338]">Credit Retirements by Quarter</h2>
            <p className="text-xs text-[#676879] mt-0.5">Mt CO₂e — ACCU, LGC, and international VCU</p>
          </div>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={RETIREMENTS_BY_QUARTER} barSize={18} barGap={3}>
              <XAxis dataKey="quarter" tick={{ fontSize: 11, fill: '#676879' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#676879' }} axisLine={false} tickLine={false} unit=" Mt" width={48} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: 11, color: '#676879', paddingTop: 12 }} />
              <Bar dataKey="accu" name="ACCU" fill={DARK_TEAL} radius={[3,3,0,0]} />
              <Bar dataKey="lgc" name="LGC" fill={TEAL} radius={[3,3,0,0]} />
              <Bar dataKey="vcu" name="VCU (intl)" fill="#B1DEE5" radius={[3,3,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Method breakdown + sector split */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* ACCU by method */}
          <div className="bg-white rounded-xl border border-[#e6e9ef] p-6">
            <h2 className="text-sm font-bold text-[#323338] mb-1">ACCU Retirements by Method</h2>
            <p className="text-xs text-[#676879] mb-5">Mt CO₂e — FY26 YTD</p>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={ACCU_BY_METHOD} dataKey="value" nameKey="method" cx="40%" cy="50%" outerRadius={80} innerRadius={40}>
                  {ACCU_BY_METHOD.map((e, i) => <Cell key={i} fill={e.color} />)}
                </Pie>
                <Legend
                  layout="vertical" align="right" verticalAlign="middle"
                  wrapperStyle={{ fontSize: 10, color: '#676879', lineHeight: '18px' }}
                  formatter={(val, entry: any) => `${val} (${entry.payload.value.toFixed(1)}Mt)`}
                />
                <Tooltip formatter={(v: any) => typeof v === 'number' ? `${v.toFixed(1)} Mt CO₂e` : v} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Sector breakdown */}
          <div className="bg-white rounded-xl border border-[#e6e9ef] p-6">
            <h2 className="text-sm font-bold text-[#323338] mb-1">Retirements by Sector</h2>
            <p className="text-xs text-[#676879] mb-5">Mt CO₂e total — all credit types</p>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={SECTOR_RETIREMENTS} layout="vertical" barSize={14}>
                <XAxis type="number" tick={{ fontSize: 10, fill: '#676879' }} axisLine={false} tickLine={false} unit="Mt" />
                <YAxis type="category" dataKey="sector" tick={{ fontSize: 10, fill: '#676879' }} axisLine={false} tickLine={false} width={72} />
                <Tooltip formatter={(v: any) => typeof v === 'number' ? `${v.toFixed(1)} Mt CO₂e` : v} />
                <Bar dataKey="volume" radius={[0,3,3,0]}>
                  {SECTOR_RETIREMENTS.map((e, i) => <Cell key={i} fill={e.color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top retirers table */}
        <div className="bg-white rounded-xl border border-[#e6e9ef] overflow-hidden">
          <div className="px-6 py-4 border-b border-[#e6e9ef] flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-[#323338]">Top 10 Retirement Entities</h2>
              <p className="text-xs text-[#676879] mt-0.5">By volume retired FY26 YTD (ACCU + LGC + VCU)</p>
            </div>
            <span className="text-[10px] bg-[#E2F4F5] text-[#10545D] font-bold px-2 py-1 rounded-full">CER Registry</span>
          </div>
          <div className="divide-y divide-[#f6f7fb]">
            {TOP_RETIRERS.map((r, i) => (
              <div key={r.name} className="grid grid-cols-[28px_2fr_1fr_1fr_80px] px-6 py-3 items-center gap-3 hover:bg-[#fafbff] transition-colors">
                <span className="text-xs font-bold text-[#c3c6d4]">#{i+1}</span>
                <span className="text-sm font-semibold text-[#323338]">{r.name}</span>
                <span className="text-xs text-[#676879]">{r.sector}</span>
                <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full w-fit ${
                  r.method === 'Safeguard' ? 'bg-[#ffd3d9] text-[#c0253d]' : 'bg-[#d4f4e2] text-[#007038]'
                }`}>{r.method}</span>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-1.5 rounded-full bg-[#f6f7fb]">
                    <div className="h-full rounded-full bg-[#499BA6]" style={{ width: `${(r.volume / 8.4) * 100}%` }} />
                  </div>
                  <span className="text-xs font-bold text-[#323338] w-12 text-right">{r.volume}Mt</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Data note */}
        <p className="text-[11px] text-[#c3c6d4] text-center pb-4">
          Data sourced from CER Australian National Registry of Emissions Units (ANREU), Safeguard Mechanism disclosures, and NGER public reports. Representative figures — connect live CER API for real-time updates.
        </p>
      </div>
    </div>
  )
}
