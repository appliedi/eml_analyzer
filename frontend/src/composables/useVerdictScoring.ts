import { computed, type Ref } from "vue"

import type { VerdictType } from "@/schemas"

export type RiskLevel =
  | "unknown"
  | "clean"
  | "low-risk"
  | "suspicious"
  | "high-risk"
  | "malicious"

const riskLabels: Record<RiskLevel, string> = {
  unknown: "No Verdicts",
  clean: "Clean",
  "low-risk": "Low Risk",
  suspicious: "Suspicious",
  "high-risk": "High Risk",
  malicious: "Malicious",
}

const riskColors: Record<RiskLevel, string> = {
  unknown: "text-base-content",
  clean: "text-success",
  "low-risk": "text-info",
  suspicious: "text-warning",
  "high-risk": "text-orange-500",
  malicious: "text-error",
}

const riskBorders: Record<RiskLevel, string> = {
  unknown: "border-base-300",
  clean: "border-success",
  "low-risk": "border-info",
  suspicious: "border-warning",
  "high-risk": "border-orange-500",
  malicious: "border-error",
}

const riskIcons: Record<RiskLevel, string> = {
  unknown: "",
  clean: "circle-check",
  "low-risk": "circle-info",
  suspicious: "circle-exclamation",
  "high-risk": "triangle-exclamation",
  malicious: "circle-xmark",
}

function isScoring(v: VerdictType): boolean {
  return v.name !== "URL Unshortening"
}

export function useVerdictScoring(verdicts: Ref<VerdictType[]>) {
  const scoringVerdicts = computed(() => verdicts.value.filter(isScoring))
  const maliciousCount = computed(
    () => scoringVerdicts.value.filter((v) => v.malicious).length,
  )
  const totalCount = computed(() => scoringVerdicts.value.length)
  const safeCount = computed(() => totalCount.value - maliciousCount.value)
  const safetyPercentage = computed(() => {
    if (totalCount.value === 0) return 100
    return Math.round((safeCount.value / totalCount.value) * 100)
  })

  const riskLevel = computed<RiskLevel>(() => {
    if (totalCount.value === 0) return "unknown"
    if (maliciousCount.value === 0) return "clean"
    const ratio = maliciousCount.value / totalCount.value
    if (ratio <= 0.2) return "low-risk"
    if (ratio <= 0.5) return "suspicious"
    if (ratio <= 0.75) return "high-risk"
    return "malicious"
  })

  const riskLabel = computed(() => riskLabels[riskLevel.value])
  const riskColor = computed(() => riskColors[riskLevel.value])
  const borderColor = computed(() => riskBorders[riskLevel.value])
  const riskIcon = computed(() => riskIcons[riskLevel.value])

  return {
    maliciousCount,
    totalCount,
    safeCount,
    safetyPercentage,
    riskLevel,
    riskLabel,
    riskColor,
    borderColor,
    riskIcon,
  }
}

export function verdictStyle(v: VerdictType) {
  return v.malicious
    ? {
        color: "text-error",
        border: "border-error",
        bg: "bg-error/10",
        badge: "badge-error",
        icon: "triangle-exclamation",
      }
    : {
        color: "text-success",
        border: "border-success",
        bg: "bg-success/10",
        badge: "badge-success",
        icon: "circle-check",
      }
}
