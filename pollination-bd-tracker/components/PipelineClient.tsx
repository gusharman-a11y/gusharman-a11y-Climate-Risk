'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Users, ExternalLink, Mail, ChevronDown, ChevronRight, Clock } from 'lucide-react'
import type { Company, PipelineStage } from '@/lib/types'
import { PIPELINE_STAGE_LABELS, relationshipBadge } from '@/lib/types'
import { Badge, ScorePill } from '@/components/Badge'

interface Props { companies: Company[] }

const STAGES: PipelineStage[] = ['watch', 'prospect', 'qualified', 'proposal', 'negotiation', 'mandated', 'missed']
const ACTIVE_STAGES: PipelineStage[] = ['prospect', 'qualified', 'proposal', 'negotiation']

function GoneQuietBadge({ company }: { company: Company }) {
  const stage = company.pipeline_stage as PipelineStage | null
  if (!stage || !ACTIVE_STAGES.includes(stage)) return null

  const lastDate = company.last_interaction_date
  if (!lastDate) {
    return (
      <span className="inline-flex items-center gap-1 bg-[#fff3e0] text-[#c47c00] text-[10px] font-semibold px-1.5 py-0.5 rounded-full">
        <Clock size={9} />
        No contact logged
      </span>
    )
  }

  const daysSince = Math.floor((Date.now() - new Date(lastDate).getTime()) / 86_400_000)
  if (daysSince < 60) return null

  return (
    <span className="inline-flex items-center gap-1 bg-[#fff3e0] text-[#c47c00] text-[10px] font-semibold px-1.5 py-0.5 rounded-full">
      <Clock size={9} />
      Quiet {daysSince}d
    </span>
  )
}

const STAGE_META: Record<PipelineStage, { color: string; bg: string; text: string }> = {
  watch:       { color: '#c3c6d4', bg: '#f6f7fb',  text: '#676879' },
  prospect:    { color: '#0073ea', bg: '#cce5ff',  text: '#0060c0' },
  qualified:   { color: '#a25ddc', bg: '#ede3f9',  text: '#7b3db8' },
  proposal:    { color: '#fdab3d', bg: '#fff3e0',  text: '#c47c00' },
  negotiation: { color: '#e2445c', bg: '#ffd3d9',  text: '#c0253d' },
  mandated:    { color: '#00c875', bg: '#d4f4e2',  text: '#007038' },
  missed:      { color: '#c3c6d4', bg: '#f6f7fb',  text: '#9699a6' },
}

interface Contact { name?: string; title?: string; email?: string; linkedin?: string; source?: string }
interface Contacts { company: string; ceo?: Contact; cfo?: Contact; head_of_sustainability?: Contact; as_of?: string }

function ContactRow({ role, contact }: { role: string; contact?: Contact }) {
  if (!contact?.name) return (
    <div className="flex items-start gap-2 py-1.5 border-b border-[#f6f7fb] last:border-0">
      <span className="text-[10px] font-bold text-[#c3c6d4] w-24 shrink-0 pt-0.5">{role}</span>
      <span className="text-[11px] text-[#c3c6d4] italic">Not found</span>
    </div>
  )
  return (
    <div className="flex items-start gap-2 py-1.5 border-b border-[#f6f7fb] last:border-0">
      <span className="text-[10px] font-bold text-[#676879] w-24 shrink-0 pt-0.5 uppercase tracking-wide">{role}</span>
      <div className="min-w-0 flex-1">
        <p className="text-xs font-semibold text-[#323338] leading-tight">{contact.name}</p>
        {contact.title && <p className="text-[10px] text-[#676879] leading-tight mt-0.5">{contact.title}</p>}
        <div className="flex items-center gap-2 mt-1 flex-wrap">
          {contact.email && (
            <a href={`mailto:${contact.email}`} onClick={e => e.stopPropagation()}
              className="flex items-center gap-1 text-[10px] text-[#0073ea] hover:underline">
              <Mail size={9} />{contact.email}
            </a>
          )}
          {contact.linkedin && (
            <a href={contact.linkedin} target="_blank" rel="noopener noreferrer" onClick={e => e.stopPropagation()}
              className="flex items-center gap-1 text-[10px] text-[#0073ea] hover:underline">
              <ExternalLink size={9} />LinkedIn
            </a>
          )}
        </div>
      </div>
    </div>
  )
}

function PipelineCard({ company, stageColor }: { company: Company; stageColor: string }) {
  const [showContacts, setShowContacts] = useState(false)
  const rb = relationshipBadge(company.relationship_status)
  const rawContacts = (company as any).key_contacts as string | null
  let contacts: Contacts | null = null
  try { if (rawContacts) contacts = JSON.parse(rawContacts) } catch {}

  return (
    <div
      className="bg-white rounded-lg border border-[#e6e9ef] overflow-hidden hover:border-[#0073ea]/40 hover:shadow-md transition-all"
      style={{ borderTop: `3px solid ${stageColor}` }}
    >
      <Link href={`/companies/${company.id}`} className="block p-3.5 group">
        <p className="text-sm font-semibold text-[#323338] leading-tight mb-0.5 group-hover:text-[#0073ea] transition-colors">
          {company.name}
        </p>
        {company.asx_code && <p className="text-[10px] font-mono text-[#676879] mb-2">{company.asx_code}</p>}
        <div className="flex items-center justify-between mt-2">
          <ScorePill score={company.score_overall} />
          <Badge label={rb.label} className={rb.className} />
        </div>
        {company.pipeline_notes && (
          <p className="text-[11px] text-[#676879] mt-2 line-clamp-2 leading-relaxed">{company.pipeline_notes}</p>
        )}
        <div className="mt-2">
          <GoneQuietBadge company={company} />
        </div>
      </Link>

      {/* Contact toggle */}
      <div className="px-3.5 pb-3">
        <button
          onClick={() => setShowContacts(s => !s)}
          className="w-full flex items-center gap-1.5 text-[11px] font-semibold border border-[#0073ea]/30 rounded px-2 py-1.5 transition-colors justify-center"
          style={showContacts ? { background: '#e8f0fd', color: '#0060c0' } : { color: '#0073ea' }}
        >
          <Users size={11} />
          {showContacts ? 'Hide contacts' : 'Get contact info'}
          {showContacts ? <ChevronDown size={10} /> : <ChevronRight size={10} />}
        </button>

        {showContacts && (
          <div className="mt-2 bg-[#fafbff] rounded border border-[#e6e9ef] p-2">
            {contacts ? (
              <>
                <ContactRow role="CEO" contact={contacts.ceo} />
                <ContactRow role="CFO" contact={contacts.cfo} />
                <ContactRow role="Sustainability" contact={contacts.head_of_sustainability} />
                {contacts.as_of && (
                  <p className="text-[10px] text-[#c3c6d4] mt-1.5 text-right">as of {contacts.as_of}</p>
                )}
              </>
            ) : (
              <p className="text-[11px] text-[#c3c6d4] italic text-center py-2">Contact data loading…</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default function PipelineClient({ companies }: Props) {
  const byStage = STAGES.reduce<Record<string, Company[]>>((acc, s) => {
    acc[s] = companies.filter(c => c.pipeline_stage === s)
    return acc
  }, {})

  const total = companies.filter(c => c.pipeline_stage !== 'missed').length

  return (
    <div className="flex flex-col min-h-screen">
      <div className="bg-white border-b border-[#e6e9ef] px-6 py-3 sticky top-14 z-10 flex items-center gap-3">
        <h1 className="text-base font-bold text-[#323338]">Pipeline</h1>
        <span className="text-xs text-[#676879] bg-[#f6f7fb] px-2 py-0.5 rounded-full border border-[#e6e9ef]">
          {total} active
        </span>
      </div>

      <div className="overflow-x-auto flex-1 p-5">
        <div className="flex gap-3 min-w-max items-start">
          {STAGES.map(stage => {
            const rows = byStage[stage] ?? []
            const meta = STAGE_META[stage]
            return (
              <div key={stage} className="w-64 flex-shrink-0 flex flex-col gap-2">
                <div className="flex items-center justify-between px-1">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: meta.color }} />
                    <span className="text-xs font-semibold text-[#323338]">{PIPELINE_STAGE_LABELS[stage]}</span>
                  </div>
                  <span className="text-[11px] font-bold px-1.5 py-0.5 rounded-full"
                    style={{ background: meta.bg, color: meta.text }}>{rows.length}</span>
                </div>
                <div className="flex flex-col gap-2">
                  {rows.map(company => (
                    <PipelineCard key={company.id} company={company} stageColor={meta.color} />
                  ))}
                  {rows.length === 0 && (
                    <div className="border-2 border-dashed border-[#e6e9ef] rounded-lg p-5 text-center">
                      <p className="text-xs text-[#c3c6d4]">No companies</p>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
