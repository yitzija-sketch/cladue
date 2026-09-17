# 1 Buckingham Avenue, Perth Amboy, NJ — Environmental Records Pull

**Site:** 1 Buckingham Ave, Perth Amboy, Middlesex County, NJ 08861 — Block 239, Lots 1 and 1.01
**Pulled:** 2026-09-17
**Status: INCOMPLETE — all three source systems are unreachable from this environment.**

---

## 1. Retrieval status — read this first

The three sources named in the request could not be reached. This session's outbound
network is governed by an organizational egress allowlist, and every relevant host is
denied at the proxy (HTTP 403 to `CONNECT`, i.e. policy denial, not a site outage):

| Host | Purpose | Result |
|---|---|---|
| `datamine2.state.nj.us` | NJDEP DataMiner | 403 — blocked |
| `dep.nj.gov` | NJDEP DocMiner / SRP | 403 — blocked |
| `www13.state.nj.us` | DataMiner (legacy) | 403 — blocked |
| `njparcels.com`, `njpropertyrecords.com` | parcel/deed lookup | 403 — blocked |
| `www.perthamboynj.org` | city records | 403 — blocked |

Keyword web search still works, so Section 2 reflects what search alone can corroborate.
It is not a substitute: **the RAP, its transfer history, and the biennial certification
record exist only inside DataMiner's SRP reports, which are database queries and are not
indexed by search engines.** No PDFs were downloaded — there was no reachable source to
download them from.

Deliverables 1–10 are therefore **unanswered**, not answered-as-negative. Nothing below
should be read as "the records show no problem." Section 4 is a ten-minute runbook for
someone on an unrestricted connection.

---

## 2. What is independently corroborated

Confirmed by public search:

- **The RAO amendment is real and public.** The Perth Amboy City Council agenda for the
  July 13, 2016 meeting records that EnviroTrac Environmental Services amended the
  Response Action Outcome issued 12/28/2015 — which "remains in full force and effect" —
  to correct administrative errors, issued to **One Buckingham Avenue, LLC (a.k.a. Vira
  Insight, LLC)** for **Restricted Use with Permit Requirements** for the entire site.
  This matches the background provided, including the 7/1/2016 amendment date.
- **Entity identity.** VIRA Manufacturing, Inc. and Insight Merchandising, LLC merged to
  form VIRA Insight, LLC; VIRA Insight lists Perth Amboy, NJ as a manufacturing and
  distribution location at 1 Buckingham Ave. The "a.k.a." in the RAO is a real corporate
  relationship, not a clerical alias.
- **The property is actively marketed industrial space** (Lee & Associates, Showcase,
  LoopNet listings for 1 Buckingham Ave), consistent with a post-sale repositioning.

Unverified lead, flagged as such: a search snippet referenced a deed for 1 Buckingham Ave
recorded at **Book 18811, Page 322**. That is plausibly the 12/23/2021 conveyance, but it
is a snippet, not a record I retrieved — do not rely on it. The Deed Notice cited in the
background (Book 6751, Page 641, recorded 11/10/2015) could not be confirmed or pulled.

Nothing was found on **Amzak Perth Amboy OZ Property Owner LLC** in an environmental
context. Absence of search hits is meaningless here — permit transfers are not publicized.

---

## 3. Why #5 and #6 are the right questions — and the deadline that governs #5

The two priority items have a hard regulatory anchor worth having in hand before the pull.

**#5 — Permit transfer. N.J.A.C. 7:26C-7.11** governs transfer of a remedial action permit
by a statutory permittee. The rule requires that, **no later than 60 calendar days after
the sale or transfer of the property**, the statutory permittee apply for the remedial
action permit transfer. The prospective permittee must be the new owner/operator/tenant,
must acknowledge **in writing** that it accepts its responsibility as permittee, and must
satisfy the applicable financial assurance requirements. NJDEP guidance is also explicit
that the new owner must sign on as co-permittee **before** the former owner comes off the
permit.

Applied to this property: the sale closed **12/23/2021**, so the transfer application was
due on or about **2/21/2022**. If DataMiner still shows **One Buckingham Avenue, LLC** as
permittee of record, that deadline was missed by roughly four and a half years as of
today, and the permit obligations — including the certifications in #6 — have been sitting
with a seller entity that no longer owns the site. That is the finding to look for.

**#6 — Biennial certification.** A RAP permittee must submit a Remedial Action
Protectiveness / Biennial Certification Form and Report on a two-year cycle. Two failure
modes matter and they compound: a certification can be late on its own, **or** it can be
formally "current" but signed by an entity with no remaining interest in the property,
because #5 was never done. The second is the worse outcome and the easier one to miss.

Note the interaction: an unexecuted transfer is not a paperwork nit. It leaves the
permittee of record, the entity with site control, and the party carrying financial
assurance as three different answers — which is exactly the exposure that matters when
current ownership is asking someone else to absorb environmental responsibility.

*(Regulatory citations above are from NJDEP guidance surfaced in search; confirm against
the Soil Remedial Action Permit Guidance Document and the rule text before relying on the
60-day figure in correspondence.)*

---

## 4. Runbook — exact steps to finish this pull

### NJDEP DataMiner — `datamine2.state.nj.us/dep/DEP_OPRA`
1. **Site Remediation → Site Search Reports → "All CSRR Sites by Selected PI Address."**
   Search `Buckingham` as street, Perth Amboy, Middlesex. Search the street name alone —
   the house number is stored inconsistently and "1" vs "One" will drop the record.
2. If that returns nothing, run **"…by Selected PI Name"** for each of: `One Buckingham
   Avenue`, `Vira Insight`, `Vira Manufacturing`, `Buckingham Property Owner`, `Amzak`.
   Use partial strings — the name field is not normalized.
3. **Capture the PI (Program Interest) number.** Everything else keys off it.
4. Run **SRP Site Detail** for that PI → full case history, permit record, CEA fact sheet.
   This single report answers #1, #4, #7, #8, #9 and most of #10.
5. Run **"Cases Requiring Remedial Action Permits"** and **"Biennial Certifications
   Overdue."** Appearance on the second report is a direct, citable answer to #6. Appearance
   on the first without a corresponding issued permit is its own problem.
6. On the permit record, read the **permittee name** field, not the site name — that is #5.
   Compare it against Amzak Perth Amboy OZ Property Owner LLC.

### NJDEP DocMiner — `dep.nj.gov/docminer`
Search the address and all four entity names; download every PDF. Expect the 12/28/2015
RAO (#2), the 7/1/2016 amendment (#2), the RAP and any modifications (#4), biennial
certification submittals (#6), and any CEA documentation (#9).

### Middlesex County Clerk
Pull **Book 6751, Page 641** (Deed Notice, recorded 11/10/2015) for #3. While there, pull
the 12/23/2021 deed to confirm the grantee entity name exactly as recorded — the permit
transfer, if one was ever filed, has to match it.

### Flag conditions
- Permittee of record still reads One Buckingham Avenue, LLC or Vira Insight, LLC → **#5 failed**, transfer overdue since ~2/21/2022.
- Site appears on "Biennial Certifications Overdue" → **#6 failed**, cite the report directly.
- Most recent biennial certification predates 12/2021 → obligation likely never picked up post-sale.
- Any open enforcement action or NON → **#10**, pull the document.

---

## 5. Deliverables status

| # | Item | Status |
|---|---|---|
| 1 | PI number and case status | **Not retrieved** — DataMiner blocked |
| 2 | RAO (12/28/2015) + amendment (7/1/2016) | **Not retrieved** — existence corroborated via city council agenda; documents not obtained |
| 3 | Recorded Deed Notice (Bk 6751 Pg 641) | **Not retrieved** — county clerk not reachable |
| 4 | Current Remedial Action Permit (soil/GW) | **Not retrieved** |
| 5 | **Whether RAP was transferred post-12/2021** | **Not retrieved — highest priority; 60-day deadline was ~2/21/2022** |
| 6 | **Most recent biennial certification / overdue?** | **Not retrieved — highest priority** |
| 7 | Current LSRP of record | **Not retrieved** (EnviroTrac was the 2015–16 firm; no evidence it is still of record) |
| 8 | Contaminants of concern / engineering control areas | **Not retrieved** |
| 9 | Classification Exception Area and boundaries | **Not retrieved** |
| 10 | Open enforcement actions / NONs | **Not retrieved** |

**PDFs downloaded: none.** Note that this repository's `.gitignore` excludes `*.pdf`; if
the pull is re-run here after egress is opened, that rule needs an exception for this
folder or the documents will be silently uncommitted.

## 6. To actually finish this

Either re-run Section 4 from an unrestricted connection, or have the egress policy for
this environment extended to `datamine2.state.nj.us`, `dep.nj.gov`, and the Middlesex
County Clerk's records host — then re-run this task as-is.
