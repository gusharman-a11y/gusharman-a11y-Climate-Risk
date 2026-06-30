import MarketIntelClient from '@/components/MarketIntelClient'
import { sbCarbon } from '@/lib/supabase-carbon'

export const dynamic = 'force-dynamic'
export const revalidate = 3600 // re-fetch every hour

export interface SafeguardRow {
  company_name: string
  accus_surrendered: number
  safeguard_emissions: number
}

function classifySector(name: string): string {
  const n = name.toUpperCase()
  if (/COAL|MINING|COLLIERY|COLLIERIES|KESTREL|ASHTON|WARKWORTH|OAKY|FITZROY|STANMORE|PEMBROKE|DENDROBIUM|METROPOLITAN/.test(n)) return 'Coal Mining'
  if (/WOODSIDE|CHEVRON|ESSO|SANTOS|OIL|GAS|PETROLEUM|LNG/.test(n)) return 'Oil & Gas'
  if (/IRON ORE|HAMERSLEY|BHP IRON/.test(n)) return 'Iron Ore'
  if (/QANTAS|VIRGIN|AIRWAYS|AIRLINES/.test(n)) return 'Aviation'
  if (/ALUMIN|ALCOA/.test(n)) return 'Aluminium'
  if (/CEMENT|BORAL|HANSON/.test(n)) return 'Cement'
  if (/ORICA|CHEMICAL|INCITEC/.test(n)) return 'Chemicals'
  if (/STEEL|BLUESCOPE|ONESTEEL/.test(n)) return 'Steel'
  if (/COPPER|NICKEL|ZINC|GOLD|SILVER|MINERAL/.test(n)) return 'Metals'
  if (/ELECTRICITY|POWER|ENERGY|AGL|ORIGIN|NRG/.test(n)) return 'Electricity'
  return 'Other Industrial'
}

export default async function MarketIntelligencePage() {
  const { data, error } = await sbCarbon
    .from('prospects')
    .select('company_name,accus_surrendered,safeguard_emissions')
    .eq('source', 'safeguard')
    .order('accus_surrendered', { ascending: false })

  const rows: SafeguardRow[] = (data ?? []) as SafeguardRow[]
  const buyers = rows.filter(r => r.accus_surrendered > 0)
  const totalACCUs = buyers.reduce((s, r) => s + r.accus_surrendered, 0)
  const totalEmitters = rows.length
  const totalEmissions = rows.reduce((s, r) => s + (r.safeguard_emissions || 0), 0)
  const avgIntensity = totalEmissions > 0 ? Math.round((totalACCUs / totalEmissions) * 100) : 0

  // Sector rollup
  const sectorMap: Record<string, number> = {}
  for (const r of buyers) {
    const s = classifySector(r.company_name)
    sectorMap[s] = (sectorMap[s] ?? 0) + r.accus_surrendered
  }
  const sectors = Object.entries(sectorMap)
    .map(([sector, volume]) => ({ sector, volume }))
    .sort((a, b) => b.volume - a.volume)

  const top15 = buyers.slice(0, 15)

  return (
    <MarketIntelClient
      totalACCUs={totalACCUs}
      totalEmitters={totalEmitters}
      buyerCount={buyers.length}
      avgIntensity={avgIntensity}
      sectors={sectors}
      topRetirers={top15}
      fetchError={error?.message ?? null}
    />
  )
}
