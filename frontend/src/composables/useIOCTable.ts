import { computed, type Ref } from 'vue'

import type { DetailType, ResponseType, StatusType } from '@/schemas'

export type IOCType = 'url' | 'domain' | 'ip' | 'email' | 'sha256'

export type CellState = 'flagged' | 'clean' | 'errored' | 'na'

export interface IOCServiceResult {
  state: CellState
  detail?: DetailType
}

export interface IOCRow {
  ioc: string
  type: IOCType
  services: Map<string, IOCServiceResult>
  isMalicious: boolean
}

interface ServiceDef {
  name: string
  label: string
  covers: IOCType[]
  /** Key in StatusType that enables this service, or null if always-on */
  statusKey: keyof StatusType | null
}

const PER_IOC_SERVICES: ServiceDef[] = [
  { name: 'urlscan.io', label: 'urlscan', covers: ['url'], statusKey: 'urlscan' },
  { name: 'IPQS URL', label: 'IPQS URL', covers: ['url', 'domain'], statusKey: 'ipqs' },
  { name: 'IPQS IP', label: 'IPQS IP', covers: ['ip'], statusKey: 'ipqs' },
  { name: 'IPQS Email', label: 'IPQS Email', covers: ['email'], statusKey: 'ipqs' },
  { name: 'Homoglyph Detection', label: 'Homoglyph', covers: ['domain'], statusKey: null },
  { name: 'URL Unshortening', label: 'Unshorten', covers: ['url'], statusKey: null },
  { name: 'VirusTotal', label: 'VT', covers: ['sha256'], statusKey: 'vt' }
]

const SENTINEL_KEYS = new Set(['benign', 'clean', 'no_resolve'])

const TYPE_ORDER: Record<IOCType, number> = {
  url: 0,
  domain: 1,
  ip: 2,
  email: 3,
  sha256: 4
}

export function useIOCTable(response: Ref<ResponseType>, status: Ref<StatusType>) {
  // Show columns for services that should have run: API configured or always-on
  const columns = computed(() => {
    return PER_IOC_SERVICES.filter(
      (s) => s.statusKey === null || status.value[s.statusKey] === true
    )
  })

  const rows = computed<IOCRow[]>(() => {
    const activeColumns = columns.value
    if (activeColumns.length === 0) return []

    // 1. Collect unique IOCs with types from bodies + attachments
    const iocMap = new Map<string, IOCType>()

    for (const body of response.value.eml.bodies) {
      for (const url of body.urls) iocMap.set(url, 'url')
      for (const domain of body.domains) iocMap.set(domain, 'domain')
      for (const ip of body.ipAddresses) iocMap.set(ip, 'ip')
      for (const email of body.emails) iocMap.set(email, 'email')
    }
    for (const att of response.value.eml.attachments) {
      iocMap.set(att.hash.sha256, 'sha256')
    }

    if (iocMap.size === 0) return []

    // 2. Track which verdicts actually returned, and build detail index
    const returnedVerdicts = new Set(response.value.verdicts.map((v) => v.name))
    const detailIndex = new Map<string, Map<string, DetailType>>()
    for (const verdict of response.value.verdicts) {
      if (!activeColumns.some((c) => c.name === verdict.name)) continue

      const keyMap = new Map<string, DetailType>()
      for (const detail of verdict.details) {
        if (!SENTINEL_KEYS.has(detail.key)) {
          keyMap.set(detail.key, detail)
        }
      }
      detailIndex.set(verdict.name, keyMap)
    }

    // 3. Build rows
    const result: IOCRow[] = []
    for (const [ioc, type] of iocMap) {
      const services = new Map<string, IOCServiceResult>()
      let isMalicious = false

      for (const svc of activeColumns) {
        if (!svc.covers.includes(type)) {
          // Service doesn't cover this IOC type
          services.set(svc.name, { state: 'na' })
          continue
        }

        if (!returnedVerdicts.has(svc.name)) {
          // Service was expected to run but verdict is missing (error/quota)
          services.set(svc.name, { state: 'errored' })
          continue
        }

        const verdictDetails = detailIndex.get(svc.name)
        if (!verdictDetails) {
          services.set(svc.name, { state: 'clean' })
          continue
        }

        const detail = verdictDetails.get(ioc)
        if (detail) {
          services.set(svc.name, { state: 'flagged', detail })
          isMalicious = true
        } else {
          services.set(svc.name, { state: 'clean' })
        }
      }

      result.push({ ioc, type, services, isMalicious })
    }

    // 4. Sort: malicious first, then by type order, then alphabetical
    result.sort((a, b) => {
      if (a.isMalicious !== b.isMalicious) return a.isMalicious ? -1 : 1
      const typeA = TYPE_ORDER[a.type]
      const typeB = TYPE_ORDER[b.type]
      if (typeA !== typeB) return typeA - typeB
      return a.ioc.localeCompare(b.ioc)
    })

    return result
  })

  const totalCount = computed(() => rows.value.length)
  const maliciousCount = computed(() => rows.value.filter((r) => r.isMalicious).length)

  return {
    rows,
    columns,
    totalCount,
    maliciousCount
  }
}
