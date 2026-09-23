# Release validation

Checked September 10, 2026 using Python 3.12.

The event and shot feeds were reconciled before building summaries. Of 1,230 source games, 1,212 pass the event/shot and scoring checks, yielding 2,424 team-game records. The exclusion file is included.

All **four automated tests passed**: offensive-rebound denominator, audited game membership, opponent defensive-rebound reconciliation and shot-location totals. The review notebook executed all four code cells without errors and recalculated the pooled offensive-rebound rate and effective field-goal percentage.

The package includes three completed scouting sheets, each in Markdown and standalone HTML, plus three PNG and three SVG figures. The figures were visually reviewed and the exported files checked for valid embedded images and local links.

Rates use player rebounds and estimated possessions, with the definitions supplied in METHODS.md and on the sheets. These checks do not convert the statistical summaries into completed film coding or validated tactical recommendations.
