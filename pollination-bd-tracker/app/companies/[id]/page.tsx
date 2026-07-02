import { getCompany, getSignals } from '@/lib/data'
import CompanyProfileClient from '@/components/CompanyProfileClient'
import { notFound } from 'next/navigation'
import { sbCarbon } from '@/lib/supabase-carbon'
import type { SafeguardPosition } from '@/lib/types'

export const dynamic = 'force-dynamic'

const LEGAL_SUFFIXES = new Set([
  'incorporated','corporation','company','limited','holdings','group',
  'inc','corp','co','ltd','llc','plc','llp','lp','pty','and','australia',
  'operations','management','energy',
])

function normKey(name: string): string {
  let s = name.toLowerCase().trim().replace(/&/g,' and ').replace(/[.,/()\-_]/g,' ').replace(/[^a-z0-9 ]/g,'')
  return s.split(/\s+/).filter(t => t && !LEGAL_SUFFIXES.has(t)).join(' ').trim()
}

async function fetchSafeguard(companyName: string): Promise<SafeguardPosition | null> {
  try {
    const { data, error } = await sbCarbon
      .from('prospects')
      .select('company_name,accus_surrendered,smcs_surrendered,net_emissions,safeguard_emissions,safeguard_baseline,compliance_strategy,surrendered_by_method')
      .eq('source', 'safeguard')
    if (error || !data || data.length === 0) return null

    const ck = normKey(companyName)
    if (!ck) return null

    // Exact match
    let match = data.find((p: SafeguardPosition) => normKey(p.company_name) === ck) ?? null

    // Prefix match
    if (!match) {
      const candidates = data.filter((p: SafeguardPosition) => {
        const pk = normKey(p.company_name)
        return pk && (pk.startsWith(ck) || ck.startsWith(pk))
      }) as SafeguardPosition[]
      if (candidates.length === 1) {
        match = candidates[0]
      } else if (candidates.length > 1) {
        match = candidates.reduce((best, c) =>
          (c.accus_surrendered ?? 0) > (best.accus_surrendered ?? 0) ? c : best
        )
      }
    }

    return match as SafeguardPosition | null
  } catch {
    return null
  }
}

export default async function CompanyPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const [company, signals] = await Promise.all([getCompany(id), getSignals(id)])
  if (!company) notFound()
  const safeguard = await fetchSafeguard(company.name)
  return <CompanyProfileClient company={company} signals={signals} safeguard={safeguard} />
}
