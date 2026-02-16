import type { IndicatorType, LinkType } from '@/schemas'
import { buildURL } from '@/utils'

class IPQualityScore implements LinkType {
  public baseURL: string
  public favicon: string
  public name: string
  public type: IndicatorType

  public constructor() {
    this.baseURL = 'https://www.ipqualityscore.com'
    this.favicon = `https://t0.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=${this.baseURL}`
    this.name = 'IPQualityScore'
    this.type = 'ip'
  }

  public href(value: string): string {
    return value
  }
}

export class IPQualityScoreForIP extends IPQualityScore {
  public constructor() {
    super()
    this.type = 'ip'
  }

  public href(value: string): string {
    return buildURL(this.baseURL, `/free-ip-lookup-proxy-vpn-test/lookup/${value}`)
  }
}

export class IPQualityScoreForURL extends IPQualityScore {
  public constructor() {
    super()
    this.type = 'url'
  }

  public href(value: string): string {
    return buildURL(this.baseURL, `/threat-intelligence/malicious-url-scanner/lookup/${encodeURIComponent(value)}`)
  }
}

export class IPQualityScoreForDomain extends IPQualityScore {
  public constructor() {
    super()
    this.type = 'domain'
  }

  public href(value: string): string {
    return buildURL(
      this.baseURL,
      `/threat-intelligence/malicious-url-scanner/lookup/${value}`
    )
  }
}

export class IPQualityScoreForEmail extends IPQualityScore {
  public constructor() {
    super()
    this.type = 'email'
  }

  public href(value: string): string {
    return buildURL(this.baseURL, `/free-email-verifier/lookup/${value}`)
  }
}
