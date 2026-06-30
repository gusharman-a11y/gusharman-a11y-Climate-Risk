'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ChevronDown, ChevronRight, Newspaper, Leaf } from 'lucide-react'
import type { Company } from '@/lib/types'
import { asrsGroupBadge, relationshipBadge } from '@/lib/types'
import { Badge, ScorePill } from '@/components/Badge'

interface Props {
  companies: Company[]
  sbtiV2Companies: Company[]
}

function SbtiPill({ status }: { status: string | null }) {
  if (!status) return <span className="text-xs text-[#c3c6d4]">—</span>
  const s = status.toLowerCase()
  const cls = s.includes('targets set') ? 'bg-[#d4f4e2] text-[#007038]' :
               s.includes('committed') && !s.includes('removed') ? 'bg-[#cce5ff] text-[#0060c0]' :
               s.includes('removed') ? 'bg-[#ffd3d9] text-[#c0253d]' :
               'bg-[#f6f7fb] text-[#676879]'
  return <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full whitespace-nowrap ${cls}`}>{status}</span>
}

function CarbonPanel({ research, news }: { research: string | null; news: string | null }) {
  let carbonData: Record<string, any> | null = null
  let newsData: Record<string, any> | null = null
  try { if (research) carbonData = JSON.parse(research) } catch {}
  try { if (news) newsData = JSON.parse(news) } catch {}

  if (!carbonData && !newsData) {
    return (
      <div className="px-6 py-4 bg-[#fafbff] border-b border-[#e6e9ef] text-xs text-[#c3c6d4] italic">
        Carbon market research pending — workflow running…
      </div>
    )
  }

  return (
    <div className="bg-[#fafbff] border-b border-[#e6e9ef] grid grid-cols-2 divide-x divide-[#e6e9ef]">
      {/* Carbon market DD */}
      <div className="px-6 py-4">
        <div className="flex items-center gap-1.5 mb-2">
          <Leaf size={12} className="text-[#00c875]" />
          <span className="text-[11px] font-bold text-[#323338] uppercase tracking-wide">Carbon Market DD</span>
        </div>
        {carbonData ? (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${carbonData.has_carbon_strategy ? 'bg-[#d4f4e2] text-[#007038]' : 'bg-[#ffd3d9] text-[#c0253d]'}`}>
                {carbonData.has_carbon_strategy ? 'Has strategy' : 'No strategy'}
              </span>
              {carbonData.confidence && (
                <span className="text-[10px] text-[#676879]">confidence: {carbonData.confidence}</span>
              )}
            </div>
            {carbonData.strategy_summary && (
              <p className="text-xs text-[#323338] leading-relaxed">{carbonData.strategy_summary}</p>
            )}
            {carbonData.credit_types_used?.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {carbonData.credit_types_used.map((t: string, i: number) => (
                  <span key={i} className="text-[10px] bg-[#e8f0fd] text-[#0060c0] px-1.5 py-0.5 rounded">{t}</span>
                ))}
              </div>
            )}
            {carbonData.estimated_volume_tco2 && (
              <p className="text-xs text-[#676879]"><span className="font-semibold">Volume:</span> {carbonData.estimated_volume_tco2}</p>
            )}
            {carbonData.key_purchases && (
              <p className="text-xs text-[#676879]"><span className="font-semibold">Purchases:</span> {carbonData.key_purchases}</p>
            )}
            {carbonData.opportunity_notes && (
              <div className="mt-2 p-2 bg-[#fff3e0] rounded border-l-2 border-[#fdab3d]">
                <p className="text-[11px] text-[#c47c00] font-semibold">Opportunity</p>
                <p className="text-xs text-[#323338] mt-0.5">{carbonData.opportunity_notes}</p>
              </div>
            )}
          </div>
        ) : (
          <p className="text-xs text-[#c3c6d4] italic">Pending…</p>
        )}
      </div>

      {/* News */}
      <div className="px-6 py-4">
        <div className="flex items-center gap-1.5 mb-2">
          <Newspaper size={12} className="text-[#0073ea]" />
          <span className="text-[11px] font-bold text-[#323338] uppercase tracking-wide">Last 6 Months</span>
          {newsData?.overall_sentiment && (
            <span className={`ml-1 text-[10px] font-bold px-1.5 py-0.5 rounded-full ${
              newsData.overall_sentiment === 'positive' ? 'bg-[#d4f4e2] text-[#007038]' :
              newsData.overall_sentiment === 'negative' ? 'bg-[#ffd3d9] text-[#c0253d]' :
              newsData.overall_sentiment === 'mixed' ? 'bg-[#fff3e0] text-[#c47c00]' :
              'bg-[#f6f7fb] text-[#676879]'
            }`}>{newsData.overall_sentiment}</span>
          )}
        </div>
        {newsData ? (
          <div className="space-y-2">
            {newsData.key_takeaway && (
              <p className="text-xs text-[#323338] font-medium leading-relaxed">{newsData.key_takeaway}</p>
            )}
            {newsData.news_items?.length > 0 && (
              <div className="space-y-1.5 mt-2">
                {newsData.news_items.slice(0, 4).map((item: any, i: number) => (
                  <div key={i} className="border-l-2 border-[#e6e9ef] pl-2">
                    <p className="text-[10px] text-[#676879]">{item.date} · <span className={`font-semibold ${
                      item.relevance === 'controversy' ? 'text-[#c0253d]' :
                      item.relevance === 'carbon_market' ? 'text-[#007038]' : 'text-[#676879]'
                    }`}>{item.relevance?.replace('_', ' ')}</span></p>
                    <p className="text-xs text-[#323338] font-medium leading-tight">{item.headline}</p>
                    {item.summary && <p className="text-[11px] text-[#676879] leading-relaxed">{item.summary}</p>}
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <p className="text-xs text-[#c3c6d4] italic">Pending…</p>
        )}
      </div>
    </div>
  )
}

function CompanyRow({ company }: { company: Company }) {
  const [expanded, setExpanded] = useState(false)
  const rb = relationshipBadge(company.relationship_status)
  const gb = asrsGroupBadge(company.asrs_group)
  const carbonResearch = (company as any).carbon_market_research as string | null
  const newsSummary = (company as any).news_6m_summary as string | null
  const hasData = !!(carbonResearch || newsSummary)

  return (
    <>
      <div
        className="grid grid-cols-[2fr_65px_100px_160px_1fr_120px_36px] px-6 py-0 gap-3 border-b border-[#e6e9ef] hover:bg-[#e8f0fd]/20 transition-colors items-stretch cursor-pointer"
        onClick={() => setExpanded(e => !e)}
      >
        <div className="flex flex-col justify-center py-3 min-w-0">
          <Link
            href={`/companies/${company.id}`}
            onClick={e => e.stopPropagation()}
            className="text-sm font-semibold text-[#323338] hover:text-[#0073ea] truncate leading-tight"
          >
            {company.name}
          </Link>
          {company.sector && <p className="text-[11px] text-[#676879] mt-0.5 truncate">{company.sector}</p>}
        </div>
        <div className="flex items-center"><ScorePill score={company.score_overall} /></div>
        <div className="flex items-center"><Badge label={gb.label} className={gb.className} /></div>
        <div className="flex items-center"><SbtiPill status={company.sbti_status} /></div>
        <div className="flex items-center min-w-0">
          <p className="text-xs text-[#676879] truncate">{company.top_signal ?? '—'}</p>
        </div>
        <div className="flex items-center">
          <Badge label={rb.label} className={rb.className} />
        </div>
        <div className="flex items-center justify-center">
          <span className="text-[#c3c6d4]">
            {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          </span>
          {hasData && !expanded && (
            <span className="w-1.5 h-1.5 rounded-full bg-[#00c875] absolute ml-3 mt-[-8px]" />
          )}
        </div>
      </div>
      {expanded && (
        <CarbonPanel research={carbonResearch} news={newsSummary} />
      )}
    </>
  )
}

export default function HotSheetClient({ companies }: Props) {
  return (
    <div>
      {/* Page header */}
      <div className="bg-white border-b border-[#e6e9ef] px-6 py-3 flex items-center justify-between sticky top-14 z-10">
        <div className="flex items-center gap-3">
          <h1 className="text-base font-bold text-[#323338]">Hot Sheet</h1>
          <span className="text-xs text-[#676879] bg-[#f6f7fb] px-2 py-0.5 rounded-full border border-[#e6e9ef]">
            {companies.length} prospects
          </span>
        </div>
        <p className="text-xs text-[#676879]">Click any row to expand carbon market DD & news</p>
      </div>

      {/* Column headers */}
      <div className="sticky top-[105px] z-10 bg-[#f6f7fb] border-b border-[#e6e9ef] grid grid-cols-[2fr_65px_100px_160px_1fr_120px_36px] px-6 py-2 gap-3">
        {['Company', 'Score', 'ASRS Group', 'SBTi', 'Top Signal', 'Relationship', ''].map(h => (
          <span key={h} className="text-[11px] font-semibold text-[#676879] uppercase tracking-wide">{h}</span>
        ))}
      </div>

      {companies.map(c => <CompanyRow key={c.id} company={c} />)}

      {companies.length === 0 && (
        <div className="flex items-center justify-center py-32 text-[#676879]">
          <p className="text-sm">No hot sheet companies configured.</p>
        </div>
      )}
    </div>
  )
}
