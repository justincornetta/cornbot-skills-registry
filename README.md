# Cornbot Skills Registry

Shareable exports of Justin Cornetta’s reusable agent skills. The repository starts with one skill and can grow as additional skills are prepared for distribution.

| Skill | What it does |
| --- | --- |
| [JMJ Capital 13F](skills/jmj-capital-13f/SKILL.md) | Creates navy-and-gold portfolio allocation and comparison graphics using the recipient’s own Robinhood connection and local snapshots. |

## Install in Codex

Clone this repository, then copy the desired **entire skill folder** into `~/.agents/skills/` for user-wide discovery, or `.agents/skills/` inside a project. For this first skill, copy `skills/jmj-capital-13f/`. Open a new Codex chat, invoke `$jmj-capital-13f`, and follow its setup reference.

A Notion connection is not needed for the exported skill. The recipient supplies their own Robinhood authentication. Python 3.10+ and Node.js 20.9+ are needed for the included helpers. Run `npm ci` from the installed skill folder before PNG export.

## Offline demonstration

From `skills/jmj-capital-13f/`:

```sh
npm ci
python3 examples/make_demo.py /tmp/cornbot-portfolio-demo
node scripts/export_pngs.mjs /tmp/cornbot-portfolio-demo/rendered
```

The demo creates fictional snapshots and validates the comparison and rendering helpers. It does not connect to Robinhood. Generated examples in `assets/` show the visual style with synthetic values.

## Adding skills

Add each reviewed, self-contained package under `skills/<skill-name>/`. Include its full `SKILL.md` and required references, scripts and assets. Replace machine-specific paths and private-document dependencies. Use invented examples; never add live holdings, histories, account identifiers, credentials, personal reference graphics or generated customer output. Do not automatically mirror the owner’s installed skills directory.

These are distribution copies. The owner’s installed skill pointers and canonical Notion instructions remain separate; this repository does not sync them automatically. Only JMJ Capital 13F has been exported so far.

## Assets and use

JMJ Capital branding is retained. Company and cryptocurrency logos remain the property of their respective owners; provenance is recorded in the skill’s `assets/logos/sources.json`. No open-source license is granted by this initial private export. Review asset rights before public redistribution.
