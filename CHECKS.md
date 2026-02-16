# Analysis Checks & Scoring

When you upload an EML or MSG file, EML Analyzer runs a series of security checks concurrently. Each check produces a **verdict** with a name, a malicious/clean status, an optional score, and detail findings.

There are two categories of checks:

- **Always-on checks** (6) run with no external configuration needed beyond SpamAssassin
- **API-key checks** (up to 6) activate when you configure the corresponding API key in your environment

Additionally, **URL Unshortening** only runs when the email body contains URLs from known shortener services.

See [README.md](README.md) for setup instructions and [ENV.md](ENV.md) for the full list of environment variables.

---

## Reading Your Results

### Overall Risk Level

The overall risk indicator combines all verdicts into a single assessment:

| Level | Condition | Color |
|---|---|---|
| Clean | 0 malicious verdicts | Green |
| Suspicious | Less than 50% malicious | Yellow |
| Malicious | 50% or more malicious | Red |
| No Verdicts | No checks produced results | Gray |

The safety percentage is calculated as:

```
Safety % = (clean count / total count) x 100
```

Checks that return no result (e.g., DKIM when there is no DKIM-Signature header) are excluded entirely — they do not count as clean or malicious.

### Verdict Summary Grid

Each verdict appears as a pill badge showing:

- A check icon (clean) or warning icon (malicious)
- The check name
- A score badge (the numeric score, or "N/A" if the check doesn't produce one)

### Verdict Detail Cards

Each verdict expands into a card showing its detail findings. Cards have a colored left border: green for clean, yellow for malicious. Each detail entry includes a description and optionally a reference link to the external service.

---

## Quick Reference

| Check | What It Does | Requires | Scored? | Malicious When |
|---|---|---|---|---|
| [SpamAssassin](#spamassassin) | Spam scoring via rule matching | SpamAssassin service | Yes (float) | Score > 5.0 |
| [OleID](#oleid) | Scans attachments for macros/exploits | Nothing extra | No | Any OLE indicator found |
| [DKIM](#dkim) | Verifies DKIM signature | Nothing extra | Yes (0 or 100) | Signature verification fails |
| [Email Authentication](#email-authentication) | Checks SPF/DKIM/DMARC results | Nothing extra | Yes (0-100) | SPF or DMARC = fail/softfail |
| [Homoglyph Detection](#homoglyph-detection) | Detects lookalike domains | Nothing extra | No | Punycode, mixed scripts, or confusables found |
| [URL Unshortening](#url-unshortening) | Expands shortened URLs | Nothing extra | No | Never (informational only) |
| [EmailRep](#emailrep) | Sender reputation lookup | `EMAIL_REP_API_KEY` | No | Sender marked suspicious |
| [VirusTotal](#virustotal) | AV scan of attachments | `VIRUSTOTAL_API_KEY` | Yes (100) | Any AV engine flags a file |
| [urlscan.io](#urlscanio) | URL reputation scanning | `URLSCAN_API_KEY` | Yes (100) | Any URL has malicious verdict |
| [IPQS IP](#ipqs-ip) | IP fraud scoring | `IPQUALITYSCORE_API_KEY` | Yes (fraud score) | Fraud score > 75 |
| [IPQS URL](#ipqs-url) | URL/domain risk scoring | `IPQUALITYSCORE_API_KEY` | Yes (risk score) | Risk score > 75 or unsafe=true |
| [IPQS Email](#ipqs-email) | Sender email fraud scoring | `IPQUALITYSCORE_API_KEY` | Yes (fraud score) | Fraud score > 75 |

Checks that return "None" (no result) are excluded from the verdict list entirely. This happens when the check has no relevant data to analyze (e.g., no DKIM header, no shortened URLs, no authentication results).

---

## Check Details

### SpamAssassin

> **Scores the email against SpamAssassin's rule database.** Each matching rule contributes a positive or negative score. A total score above 5.0 indicates likely spam.

**Verdict name:** `SpamAssassin`
**Requires:** SpamAssassin service (runs via Docker in local dev, as a sidecar in production)
**Malicious when:** Total score > 5.0
**Score:** Float — the cumulative SpamAssassin score

The raw email is sent to SpamAssassin for analysis. SpamAssassin evaluates it against hundreds of rules covering content patterns, header anomalies, Bayesian analysis, and DNS blocklists. Each triggered rule is listed as a detail finding with its rule name, individual score contribution, and description (e.g., `URIBL_BLOCKED`, `HTML_MESSAGE`, `SPF_PASS`). The verdict score is the sum of all rule scores. A score of `None` from SpamAssassin is also treated as spam.

---

### OleID

> **Scans email attachments for suspicious OLE (Object Linking and Embedding) indicators.** Detects VBA macros, XLM macros, Flash objects, encryption, external relationships, and ObjectPool streams — all common vectors for malware delivery.

**Verdict name:** `oleid`
**Requires:** Nothing extra (uses the oletools library)
**Malicious when:** Any OLE indicator is found in any attachment
**Score:** None

Each attachment is decoded and analyzed using OleID. The check looks for six specific indicators:

- **VBA macros** — Visual Basic for Applications code (common malware payload)
- **XLM macros** — Excel 4.0 macros (legacy but still abused)
- **Flash objects** — Embedded Flash content (exploitation vector)
- **Encryption** — Password-protected files (used to evade scanning)
- **External relationships** — Links to external resources (potential for remote code execution)
- **ObjectPool** — OLE ObjectPool stream (can contain embedded executables)

Detail findings include the filename and SHA-256 hash. If no indicators are found, the verdict is clean with the message "There is no suspicious OLE file in attachments." Individual attachment parsing errors are silently caught — a single corrupt attachment won't prevent other attachments from being analyzed.

---

### DKIM

> **Verifies the email's DKIM cryptographic signature.** A valid DKIM signature proves the email hasn't been tampered with in transit and genuinely originated from the claimed sending domain.

**Verdict name:** `DKIM`
**Requires:** Nothing extra (performs DNS lookups for the public key)
**Malicious when:** DKIM signature verification fails
**Score:** 0 (valid) or 100 (invalid)

The check first looks for a `DKIM-Signature` header. If none exists, the check returns no result (None) and is excluded from verdicts entirely — this is not treated as a failure. When a signature is present, the raw email bytes are verified against the sender's public key retrieved via DNS. A successful verification produces a clean verdict; a failed verification (invalid signature, missing DNS record, or key mismatch) produces a malicious verdict.

---

### Email Authentication

> **Evaluates SPF, DKIM, and DMARC authentication results from the email headers.** These protocols verify that the sending server was authorized to send on behalf of the claimed domain. Also performs a DNS lookup for the sender domain's published DMARC policy.

**Verdict name:** `Email Authentication`
**Requires:** Nothing extra (parses existing headers + DNS lookup)
**Malicious when:** SPF or DMARC result is `fail` or `softfail`
**Score:** Per-method severity (0-100), verdict score = max of all method scores

Each SPF, DKIM, and DMARC result is assigned a severity score:

| Result | Score | Meaning |
|---|---|---|
| `pass` | 0 | Fully authenticated |
| `none` | 25 | No record configured |
| `neutral` | 25 | Neither pass nor fail |
| `temperror` | 25 | Temporary DNS error |
| `permerror` | 50 | Permanent DNS error |
| `policy` | 50 | Policy decision |
| `softfail` | 75 | Domain discourages but doesn't reject |
| `fail` | 100 | Domain explicitly rejects |

The verdict-level score is the maximum of all individual method scores (worst result wins). The DMARC policy detail does not carry a score.

This check parses `Authentication-Results` headers to extract SPF, DKIM, and DMARC results. It recognizes the following result values: `pass`, `fail`, `softfail`, `neutral`, `none`, `temperror`, `permerror`, `policy`. Only SPF and DMARC failures trigger a malicious verdict — a DKIM failure in the Authentication-Results header alone does not (use the dedicated DKIM check for signature verification).

The check also performs a DNS TXT lookup for `_dmarc.<sender-domain>` to retrieve the published DMARC policy (`none`, `quarantine`, or `reject`), which is included as a detail finding.

If neither Authentication-Results headers nor a sender domain are available, the check returns None and is excluded from verdicts.

---

### Homoglyph Detection

> **Detects lookalike domains that use visual tricks to impersonate legitimate domains.** Catches punycode-encoded internationalized domain names, mixed-script attacks (e.g., Latin mixed with Cyrillic), and individual characters that are visually confusable with common Latin characters.

**Verdict name:** `Homoglyph Detection`
**Requires:** Nothing extra (uses the confusable-homoglyphs library)
**Malicious when:** Any punycode, mixed-script, or confusable character is detected
**Score:** None

This check analyzes all domains found in the email body plus the sender's domain (extracted from the From header). For each domain, it performs three tests:

1. **Punycode detection** — Identifies domains with `xn--` labels and decodes them to reveal the actual Unicode characters
2. **Mixed-script detection** — Flags domains that combine characters from different scripts (e.g., mixing Latin "a" with Cyrillic "а")
3. **Confusable character detection** — Identifies individual characters that look similar to characters from other scripts

This check always produces a verdict (never returns None). If no issues are found, the verdict is clean.

---

### URL Unshortening

> **Expands shortened URLs to reveal their true destinations.** This is purely informational — it doesn't judge whether the destination is malicious, but exposes where shortened links actually lead so other checks (urlscan.io, IPQS) can evaluate the real URLs.

**Verdict name:** `URL Unshortening`
**Requires:** Nothing extra (follows HTTP redirects)
**Malicious when:** Never — always `malicious=false` (informational only)
**Score:** None

The check filters all URLs found in the email body against a list of ~30 known URL shortener domains including bit.ly, t.co, tinyurl.com, goo.gl, ow.ly, is.gd, rb.gy, and others. Each shortened URL is resolved by following HTTP redirects (HEAD request, 5-second timeout). Detail findings show the mapping from the original shortened URL to its final destination.

If no URLs from known shortener services are found in the email, the check returns None and is excluded from verdicts. Resolution failures for individual URLs are silently caught.

---

### EmailRep

> **Checks the sender's email address against EmailRep's reputation database.** EmailRep aggregates data from breach databases, social media profiles, and other sources to assess whether an email address is likely legitimate or suspicious.

**Verdict name:** `EmailRep`
**Requires:** `EMAIL_REP_API_KEY` environment variable
**Malicious when:** EmailRep flags the sender as `suspicious=true`
**Score:** None

The sender's email address (from the From header) is looked up via the EmailRep API. The detail finding includes a link to the full EmailRep report at `emailrep.io/<email>`. This check only runs when both the `EMAIL_REP_API_KEY` is configured and a From header is present.

---

### VirusTotal

> **Checks email attachments against VirusTotal's database of antivirus engine results.** Looks up each attachment by its SHA-256 hash — does not upload files. A detection by any AV engine triggers a malicious verdict.

**Verdict name:** `VirusTotal`
**Requires:** `VIRUSTOTAL_API_KEY` environment variable
**Malicious when:** Any antivirus engine reports a file as malicious
**Score:** 100 when malicious; detail entries show the count of malicious detections per file

Each attachment's SHA-256 hash is looked up against VirusTotal's file database. If VirusTotal has analyzed the file before, the number of AV engines flagging it as malicious is reported. Detail findings include the SHA-256 hash, the detection count (e.g., "5 reports say <hash> is malicious"), and a link to the VirusTotal detection page. Multiple attachments are checked concurrently. If no attachments have detections (or VirusTotal has no record of the files), the verdict is clean.

---

### urlscan.io

> **Scans all URLs found in the email body against urlscan.io's database.** urlscan.io analyzes URLs for phishing, malware distribution, and other malicious activity.

**Verdict name:** `urlscan.io`
**Requires:** `URLSCAN_API_KEY` environment variable
**Malicious when:** Any URL has a malicious verdict from urlscan.io
**Score:** 100 when malicious

All URLs extracted from the email body are looked up against urlscan.io. Each URL flagged as malicious appears as a detail finding with a link to the urlscan.io report. Multiple URLs are checked concurrently. If no URLs are flagged, the verdict is clean with the message "There is no malicious URL in bodies."

---

### IPQS IP

> **Checks IP addresses found in the email against IPQualityScore's fraud detection database.** Identifies IPs associated with proxies, VPNs, Tor exit nodes, bots, and recent abuse.

**Verdict name:** `IPQS IP`
**Requires:** `IPQUALITYSCORE_API_KEY` environment variable
**Malicious when:** Fraud score > 75
**Score:** The fraud score for each flagged IP

Private, reserved, loopback, and link-local IP addresses (e.g., 10.x.x.x, 172.16.x.x, 192.168.x.x, 127.0.0.1, 169.254.x.x, ::1) are automatically filtered out before querying the API. All remaining global IP addresses are checked against the IPQS API. IPs with a fraud score above 75 are flagged, and the detail findings list specific risk indicators:

- **proxy** — IP is a known proxy
- **VPN** — IP is a VPN endpoint
- **Tor** — IP is a Tor exit node
- **bot** — IP shows bot activity
- **recent abuse** — IP has been recently reported for abuse

Each flagged IP includes a link to the IPQS lookup page. Multiple IPs are checked concurrently.

---

### IPQS URL

> **Checks URLs and domains from the email against IPQualityScore's threat intelligence.** Detects phishing pages, malware distribution, spam sources, and other suspicious web resources.

**Verdict name:** `IPQS URL`
**Requires:** `IPQUALITYSCORE_API_KEY` environment variable
**Malicious when:** Risk score > 75 OR `unsafe=true`
**Score:** The risk score for each flagged URL

All URLs and domains extracted from the email are combined and checked against the IPQS API. URLs meeting either threshold (risk score above 75 or explicitly marked unsafe) are flagged, with detail findings listing specific risk indicators:

- **phishing** — URL is associated with phishing
- **malware** — URL distributes malware
- **spamming** — URL is associated with spam campaigns
- **suspicious** — URL exhibits suspicious characteristics

Each flagged URL includes a link to the IPQS threat intelligence page.

---

### IPQS Email

> **Checks the sender's email address against IPQualityScore's email validation database.** Identifies disposable email addresses, honeypots, addresses involved in data breaches, and other indicators of fraudulent senders.

**Verdict name:** `IPQS Email`
**Requires:** `IPQUALITYSCORE_API_KEY` environment variable
**Malicious when:** Fraud score > 75
**Score:** The fraud score for the sender's email

The sender's email address is checked against the IPQS API. If the fraud score exceeds 75, the verdict is malicious and detail findings list specific risk indicators:

- **disposable** — Address is from a disposable email service
- **honeypot** — Address is a known honeypot/spam trap
- **recent abuse** — Address has been recently reported for abuse
- **suspect** — Address exhibits suspicious characteristics
- **leaked** — Address has appeared in data breaches

The detail finding includes a link to the IPQS email verification page.

---

## Configuration

### API Key to Check Mapping

| Environment Variable | Checks Enabled |
|---|---|
| `EMAIL_REP_API_KEY` | EmailRep |
| `VIRUSTOTAL_API_KEY` | VirusTotal |
| `URLSCAN_API_KEY` | urlscan.io |
| `IPQUALITYSCORE_API_KEY` | IPQS IP, IPQS URL, IPQS Email |

A single IPQualityScore API key enables all three IPQS checks.

### Service Status

The application header shows status indicators for configured services:

- **Green** — Service is configured and reachable
- **Yellow** — Service is unavailable or not configured

See [ENV.md](ENV.md) for the full environment variable reference.

---

## Notes for Self-Hosters

### Concurrency

All checks run concurrently using [aiometer](https://github.com/florimondmanca/aiometer). Two environment variables control rate limiting:

- `ASYNC_MAX_AT_ONCE` — Maximum number of concurrent async tasks (default: unlimited)
- `ASYNC_MAX_PER_SECOND` — Maximum tasks launched per second (default: unlimited)

These are particularly useful if you have rate-limited API keys.

### Missing Verdicts

Checks that return `None` are excluded from the results entirely. They do not count toward the risk calculation (neither clean nor malicious). This happens when a check lacks the data it needs — for example, DKIM returns None when there is no DKIM-Signature header, and URL Unshortening returns None when there are no shortened URLs.

### Error Handling

Each check is wrapped in a try/except block. If a check fails (network timeout, API error, parsing exception), it is silently dropped from the results rather than failing the entire analysis. Check the application logs for details on individual check failures.
