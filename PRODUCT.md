# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Static HTML/CSS/JS, no build step. Data comes from Python 3 scripts that write JSON into `data/processed/`. Hosting is undecided; a free static host is assumed.

## Users

General residents of Yilan County who use the internet, on phones (iOS and Android) and on desktop browsers. They want to see what their county council and its members have done, without political commentary. Added later, possibly: a second collaborator who maintains data.

## Product Purpose

Present the public record of the Yilan County Council (terms 19 and 20) as plain, objective numbers: members, bills, sessions, with a link to the original on the council's own site for every figure. Success is a resident finding a member or a bill in a few taps and being able to verify it at the source.

## Positioning

An independent, non-official reading aid for the council's published record. It states counts and dates only. It does not rank members, score them or comment.

## Operating Context

Source is the council's own site, www.ilcc.gov.tw: an old Big5-encoded ASP frameset with no open-data feed. Member list (33 listed with name, district number, party code, member ID), a bill database filterable by origin and type, and a session schedule are confirmed reachable. The bill search rejected a scripted request with HTTP 500. The 20th term's last regular session was extended to 6 November 2026 and the county election is in late November 2026.

## Capabilities and Constraints

- Members, bills, sessions for terms 19 and 20.
- Quantitative and objective only. No political judgement, no rankings.
- Party appears as text only.
- Confirmed unknown: whether roll-call votes and interpellation (質詢) text exist in structured form. Attendance and interpellation counts are only to be shown if they can be sourced; otherwise first release shows proposal counts, bill types and session volume only.
- Samples used for design so far contain invented names and numbers and must stay labelled as samples.

## Brand Commitments

Working name: 宜蘭縣議會觀測. No logo or colours exist. The site must say it is not an official council site.

## Evidence on Hand

None supplied by the user. Scraped files do not exist yet. No testimonials, endorsements or usage figures exist and none may be invented.

## Product Principles

1. Every number links to its source on the council site.
2. Counts and dates, never judgement.
3. Readable by anyone on a phone before it is impressive on a desktop.
4. Say plainly what is not known rather than leaving a gap that looks like a result.
5. Neutral to the parties: no party colours, no ordering that favours anyone.

## Accessibility & Inclusion

WCAG 2.2 AA. Traditional Chinese (zh-Hant). Works on current iOS Safari and Android Chrome. Touch targets at least 44px.
