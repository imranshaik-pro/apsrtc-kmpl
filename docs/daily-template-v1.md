# Approved daily report template: daily-v1

The owner approved the coloured Proddutur model on 2 October 2026 and asked to implement and lock its formatting. `daily-v1` retains the approved navy header, green/red KPI cards, table styles, spacing, Telugu headings, embedded Noto fonts and section order. The stylesheet/font hashes and independently captured model tables are regression fixtures. A visual change requires owner approval and a template version change; do not silently redesign the report.

## One presentation model

`src/reporting/daily_template.py` reads the completed daily text and produces both a self-contained coloured HTML report and Telegram-compatible HTML. `src/reporting/telegram_daily.py` remains the existing workflow entry point. Fetchers, KMPL calculations, slab boundaries, depot mappings and tyre-date eligibility are unchanged.

The fixed order is:

1. APSRTC / selected depot / daily report date and Telugu weekday.
2. HSD KPI cards and Target / Actual / Difference table.
3. Top 10 low-day-KMPL vehicle table, retaining each vehicle's day and Upto values.
4. Slab counts and Upto count-share note.
5. Positive tyre categories, vehicle/position tables, and dated spare snapshot.
6. Service-classification check and inspection priorities.
7. Google Drive source link and the depot-progress caption.

NAC/AC blocks use the same KPI style whenever source values exist. Unavailable values are not zero and do not generate target-performance claims. Empty tyre categories are omitted; unavailable categories stay explicitly unavailable. Historical requests remain KMPL-only. The separate spare source date must remain visible.

Target differences use Decimal half-up to two places. EX/IH percentages describe the share of Upto vehicles at or below 5.00; counts do not prove causes or contributions to the fuel-weighted depot average. Inspection wording does not invent a driver fault, mandatory tyre-removal rule or replacement-age threshold. Unknown CG classification stays unresolved; the product does not show code paths.

## Storage and delivery

Keep the original depot/date TXT as the daily source/cache. Generate a companion named `DEPOT_YYYY-MM-DD_daily-v1.html`; current requests use `_daily-v1_current.html`. Separate names prevent a historical KMPL-only view from replacing the current-request tyre snapshot. Only these HTML companions may be refreshed by `upload_daily_html`; the original cached Drive TXT is never overwritten by presentation changes.

The HTML is self-contained, including the approved fonts and their SIL Open Font License notices. Download/open it in a browser for the full coloured layout; Google Drive may offer a download rather than render an HTML page. `DRIVE_LINK` points to the styled companion, which links back to the original source TXT. Hub callbacks continue to accept the existing Drive-file URL shape. Workflow artefacts contain both TXT and HTML.

Telegram `sendMessage` uses supported `<b>` and `<pre>` formatting, status emojis and escaped source text. Fonts and colours follow the recipient's Telegram theme; arbitrary CSS/font-colour tags are not sent. The colour report remains available through the report link. Messages are bounded to 4,000 UTF-16 units including HTML, below the documented 4,096 parsed-character limit, each with balanced HTML tags; oversized tables repeat their headings without losing rows. See [Telegram formatting documentation](https://core.telegram.org/bots/api#html-style).

Existing scheduled duplicate-delivery suppression is retained. Manual requests can deliberately send the selected report again. Companions do not change the scheduled/monthly/annual source rules or merge other open work.

## Validation

The reference report is Proddutur 30 September 2026, with tyre details captured 1 October. Six approved model tables, ten low-KMPL vehicles, seventeen tyre vehicle entries and both 63-vehicle slab totals are captured in tests. All vehicle/position/tyre-number/day associations must match the approved model. The known sample fits in one Telegram message.

Checks cover the fixed style/font hashes, source-value preservation, TOT/NAC/AC, missing targets, other depot/date headings, HTML escaping, unavailable versus empty tyre results, independent spare dates, large Telegram tables, text-cache preservation, separate current/history HTML names and the HTML upload MIME type. Local validation passed: 141 daily-report checks and compilation of the changed Python modules. The generated coloured model was rendered and visually inspected; all six reference tables match exactly. The recovered real Proddutur 1 October report was also rendered, retaining available TOT/NAC/AC source values, all 70-vehicle slab totals and its separate 2 October spare snapshot. Live verification succeeded on [branch run #140](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/36991267862), tested code commit `d8465010eddd55d9a41c5dc4a70fb5e116ea9736`, on 2 October at 15:12 IST. The workflow compiled the modules, passed its 74 focused checks, reused the genuine saved 1 October KMPL report, refreshed current-request tyre details, uploaded the daily-v1 current HTML companion and received Telegram API success for two formatted messages. No Hub row was supplied, so the Hub callback was intentionally skipped; production form activation requires merging this change. Downloaded TXT/HTML artefacts were compared: the HTML exactly matches the renderer from that TXT, all eight tables retain source values, both slab totals are 70, and the sixteen tyre vehicle entries (6 mixed, 2 repair, 8 spare) keep the separate 2 October spare snapshot. The first live run revealed an unnecessary footer-only second message. A regression fixture now requires the real TOT/NAC/AC report and its footer to fit one complete message; the 4,000-unit limit preserves all rows. Live verification of that final adjustment is recorded after its rerun. [Coloured report](https://drive.google.com/file/d/1qMROIj6rDS3ZfYWUJ70rERzC29VtqP9i/view?usp=drivesdk).

## Separate source incident

The early 2 October Proddutur run for 1 October yielded zero parsed vehicle rows. The failed response HTML was not retained, so its exact upstream cause was not established. [Scheduled retry 36972310230](https://github.com/imranshaik-pro/apsrtc-kmpl/actions/runs/36972310230) subsequently generated the 1 October report and sent one Telegram message; later scheduled retries reused the saved report without duplicate delivery. No vehicle-parser change is included in this presentation work. Proddutur annual historical engine Upto remains deferred.
