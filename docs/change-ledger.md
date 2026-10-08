# Complete production commit ledger

Reviewed on 3 October 2026. This ledger contains all 295 commits reachable from production baseline 54dcf6bd760bbf60d728ce1aee8677b54021b177, from the first repository commit on 21 August through the approved daily-v1.1 merge on 2 October 2026.

Dates are recorded author timestamps in UTC. Rows follow the reversed GitHub master history listing; merged branch timestamps may interleave. Each commit link opens its complete diff. Commit subjects are preserved as history, not interpreted as certification of source correctness or external deployment.

Open draft PR #1 (historical Engine marker issue) and PR #4 (Hub callback/native logos) are not part of this production ledger. Their reviewed status and separate deployment evidence are in [action plan](roadmap-and-known-issues.md) and [project history](project-history.md). The documentation-only consolidation has a separate review commit.

| No. | UTC timestamp | Commit | Recorded change |
| --- | --- | --- | --- |
| 1 | 2026-08-21T13:19:02Z | [e3301d6](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/e3301d6046032e16dc7040786cd112b60684feb2) | Initial commit – APSRTC-KMPL project |
| 2 | 2026-08-22T01:24:50Z | [f5b4ebf](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/f5b4ebf968320c78f24f89d3ffd5d3bd8aebf9e0) | Added retry wrapper, flexible depot generator, mapping; updated cron-ready |
| 3 | 2026-08-22T01:31:36Z | [acbeb08](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/acbeb084f0c201d32cb7ef1d4b50a498251dd1d0) | Restored full wrapper with retry and Google Drive upload |
| 4 | 2026-08-22T02:00:15Z | [3989c80](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/3989c80569b56aba47192123c5998c84d90fc3e4) | Added top 10 low For‑Day vehicle list with both KMPL values |
| 5 | 2026-08-22T02:52:48Z | [114c20e](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/114c20ee13a6a42d5736b5162da952db5a102721) | Added NAC-only vehicle list with unknown type alert; included flexible depot mapping |
| 6 | 2026-08-22T06:29:24Z | [55ff66a](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/55ff66a5f2ea76cff983b8710f5f6abad75f1833) | Improved unknown vehicle alert; added HT, IU as NAC; IB, IR as AC |
| 7 | 2026-08-22T08:23:13Z | [92dca5c](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/92dca5ce6a296194b7c87f6047e5a05d693b45b1) | Full depot mapping with region codes; vehicle type mapping file; updated summary to use mapping |
| 8 | 2026-08-22T08:56:37Z | [0cd70d4](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/0cd70d41a6c691d11837f5d52ceae45e49f165e5) | Fixed Proddatur server value and Python 3.6 compatibility |
| 9 | 2026-08-22T14:03:16Z | [4fd9e2d](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/4fd9e2d0dca84dfe13cdb67150f9367a5c9b379e) | Added auto-logging of unknown operation types; treat unknown as NAC; pass depot/date to summary |
| 10 | 2026-08-22T14:05:06Z | [61c9744](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/61c9744b2a06260928d979399fea9fde7213dda1) | Added process_requests.py poller; updated .gitignore; updated depot mapping builder |
| 11 | 2026-08-24T03:51:39Z | [3ecb304](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/3ecb304e6c0aa160f4597deab41386eb142deb3f) | Added operation type column to low‑KMPL vehicle list |
| 12 | 2026-08-24T04:47:54Z | [51fb03e](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/51fb03e82011082bfb5866f729aa1515de973301) | Added slab-wise operation type table with merged rows and dynamic columns |
| 13 | 2026-08-24T13:05:07Z | [232ddae](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/232ddaee5100b78b1b6a4eef523aaefaeec892bd) | Added monthly vehicle report with formatting, dual-sheet poller support |
| 14 | 2026-08-29T03:51:20Z | [40e6475](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/40e647594ddc15f5f590948cdc88e6fe65794281) | Add GitHub Actions workflow for Docker build and push |
| 15 | 2026-08-29T04:01:04Z | [5f5cc20](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/5f5cc20897f1e3ce35a747ded157ce02b4d3724a) | Add Dockerfile and daily wrapper scripts for containerized automation |
| 16 | 2026-08-29T04:11:49Z | [b9c651b](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/b9c651bfb189e1967632030977c124e8b0b5bc11) | Add system dependencies for lxml and libffi in Dockerfile |
| 17 | 2026-08-29T04:21:02Z | [1a01935](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/1a01935c92b03a5270f0d70d22b2d3a16c30d87e) | Fix YAML indentation, add debug step, and install build deps |
| 18 | 2026-08-29T04:42:22Z | [16bce40](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/16bce40e9bd5edbc38ecb411847d7d7f345012f1) | Remove dataclasses (not needed for Python 3.9) and use flexible versions |
| 19 | 2026-08-29T04:53:59Z | [56fd1d8](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/56fd1d8e80af0ca20c39bdada8e40d3304a9f96a) | Trigger workflow |
| 20 | 2026-08-29T08:46:18Z | [7730f02](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/7730f02d828f6bd4ee87861f514b38d3ae6232b5) | Add gdrive to Docker image for upload support |
| 21 | 2026-08-29T10:20:11Z | [a742c60](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/a742c60de71901f1a90c97fb7d6149053883b37a) | Add UT operation type as NAC (Ultra Pallevelugu) |
| 22 | 2026-08-29T10:30:49Z | [069a9d9](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/069a9d960a95c85c10771c3ae3a8a1ef300f940a) | Add upload logic to generate_report.py for poller compatibility |
| 23 | 2026-08-29T11:25:23Z | [dc204ad](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/dc204ad7157edb10f69bab3fedf7bd717a0414b2) | Restore slab functions and fix import error |
| 24 | 2026-08-29T11:35:11Z | [25e42c2](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/25e42c281d54f6bb930f1b155b8b3c34368801f5) | Show raw operation type in unknown vehicle alert |
| 25 | 2026-08-29T11:42:08Z | [5f29f66](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/5f29f66cd4486fa37c12b519f41b6dd6565cea5c) | Add display names as keys for direct lookup |
| 26 | 2026-08-29T12:25:20Z | [e5bd891](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/e5bd891431fc5155f8266d374284f0b6a80654bf) | Regenerate depot mapping using official website dropdown |
| 27 | 2026-08-30T01:51:39Z | [e2042e5](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/e2042e53f61080892eecd312be7753d0433baf0f) | Save monthly report with proper filename; fix gdrive account selection |
| 28 | 2026-08-30T03:42:59Z | [28ef081](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/28ef081937a89f838851f919e9e5ae1bb76f0ae8) | Capture actual file link for monthly reports; generic VIEW_URL capture |
| 29 | 2026-08-30T09:27:45Z | [862b35f](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/862b35f500dd250139c865602b49fd800d417ac4) | Include Jan-Feb-Mar months in EXCL AC KPI report |
| 30 | 2026-09-05T06:26:14Z | [76cc8dc](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/76cc8dc02cfbc54f2c8c4a3b0b3a50ccddd3747f) | Add automation configuration for daily and monthly report folders |
| 31 | 2026-09-05T06:26:36Z | [a89cbd3](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/a89cbd38a0e03eabd5f8afe1b43ba2e5aa195882) | Add portable Google Drive integration with duplicate protection |
| 32 | 2026-09-05T06:26:52Z | [dc9e8db](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/dc9e8db2693a2b54fe7e9cd002a342e473f76cfa) | Add idempotent cloud daily report runner |
| 33 | 2026-09-05T06:27:21Z | [20bf0de](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/20bf0dea453b74808016b87f0489bd8a3716de45) | Add safe manual GitHub Actions workflow for daily reports |
| 34 | 2026-09-05T07:50:04Z | [8a983fb](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/8a983fbac4e19b7f387231dcf256e758ed448003) | Align Google Drive OAuth scope with refresh token |
| 35 | 2026-09-05T08:17:40Z | [40a537f](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/40a537f5ef8c5b8e3c82301b63c0def2dfe8234e) | Enable scheduled APSRTC daily report retries |
| 36 | 2026-09-05T08:29:02Z | [47e7487](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/47e74877a319837ca28e327892725738386ea57a) | Add native Google Sheets upload support |
| 37 | 2026-09-05T08:29:27Z | [87489dd](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/87489dd604dd526e6cb1a4002697758e23b859fd) | Run monthly reports fully in GitHub and upload as Google Sheets |
| 38 | 2026-09-05T08:29:36Z | [52b61e8](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/52b61e8620c7a15e67a316e978d9774a8d0d23b6) | Add GitHub workflow for monthly KMPL reports |
| 39 | 2026-09-05T08:30:02Z | [6b2be2b](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/6b2be2bb103137b4d7a511c68ab93f3b24c0bdc0) | Add Google Form trigger for daily reports |
| 40 | 2026-09-05T08:30:17Z | [a690113](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/a690113e5ca03fc97004cace32064d413abe7ec8) | Add Google Form trigger for monthly reports |
| 41 | 2026-09-05T09:45:10Z | [39455ca](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/39455caf0c2be850b645d895d90defc29aaa7de3) | Format monthly KMPL values to two decimals |
| 42 | 2026-09-05T09:56:40Z | [417f8f8](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/417f8f822c0912112049910c82f25d2af52b55f8) | Normalize all monthly KMPL cells to two decimals |
| 43 | 2026-09-05T10:34:33Z | [e395fa9](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/e395fa9722eb31342022ee3d7eba65b13130e7f5) | Configure annual KPI Drive folder |
| 44 | 2026-09-05T10:34:43Z | [136ef5d](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/136ef5d93aca5bf6d0e536ced18ea7130ecf7303) | Add annual KPI workflow |
| 45 | 2026-09-05T10:35:02Z | [1308ba1](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/1308ba1bad1301ced4e04703b6915310ced2dc06) | Add annual KPI Google Form trigger |
| 46 | 2026-09-05T10:36:00Z | [f0f8cf2](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/f0f8cf21d035dfd5ebca3943229b4a6e80c37a6a) | Add cloud annual KPI generator |
| 47 | 2026-09-05T10:44:47Z | [e104e7d](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/e104e7daea0630278c62b3ad6f14b39b340c48ef) | Add Google Sheets helpers for incremental annual KPI updates |
| 48 | 2026-09-05T10:45:22Z | [325fc18](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/325fc1858080b5b5b0e4dd2396439424b4e35dbf) | Add incremental annual KPI updater with tyre depot code handling |
| 49 | 2026-09-05T10:45:29Z | [9db83db](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/9db83db6be74815f12a3146ad1fd45bad52efac7) | Use incremental annual KPI updater |
| 50 | 2026-09-05T10:54:17Z | [9c3f9ea](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/9c3f9ea18de6ad9c941ca6c8944af1f5479a90ec) | Enforce exact All Tyre Sizes Total row for annual KPI |
| 51 | 2026-09-05T10:54:23Z | [b973849](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/b973849e4e645cbd40c803688fe6dbee08e2e67c) | Run annual KPI with strict tyre total-row selector |
| 52 | 2026-09-05T11:00:58Z | [0ceb265](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/0ceb265e10b1a1ce80eddc9255b61463e2ebd13b) | Mark unavailable annual KPI values for manual input |
| 53 | 2026-09-05T11:04:42Z | [7f01ec6](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/7f01ec66687eb6b7c32e3233da0bc0ab27200f67) | Derive annual KPI financial year from selected form month |
| 54 | 2026-09-05T11:04:49Z | [4d37dcd](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/4d37dcde4753e65531f97ce54e9c6982a8048b1b) | Accept selected month from annual KPI form |
| 55 | 2026-09-05T11:11:20Z | [63f03f3](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/63f03f33091ea01dc1b018b18969448e1259bae1) | Honor selected month and safely handle annual KPI source gaps |
| 56 | 2026-09-05T11:11:33Z | [20d76cc](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/20d76ccc58cff3a68c5c15eafa7d8625754b9e5c) | Pass selected month into annual KPI runner |
| 57 | 2026-09-05T11:14:14Z | [a63041a](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/a63041a91032c26112077b0f8b58316d3273d4a8) | Treat unavailable Spring source as manual input |
| 58 | 2026-09-05T11:16:43Z | [fea25bf](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/fea25bfda761e5e8d7cade055ba3d7fa40a7b4ff) | Use verified APSRTC MED breakdown and spring source paths |
| 59 | 2026-09-05T11:25:16Z | [fcdf239](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/fcdf239aff6e76eb012815c3e0edf7bca632919d) | Harden annual MED LUB and tyre KPI source validation |
| 60 | 2026-09-05T13:38:12Z | [2a76803](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/2a76803e0f9ff8d215b6a5ff2125194833b318f1) | Rebuild annual KPI dashboard with month-wise FY history |
| 61 | 2026-09-05T13:38:25Z | [8f1ad7f](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/8f1ad7f0f93ed6907faa77e780f7f2a57bba667a) | Allow first annual dashboard history build to complete |
| 62 | 2026-09-05T14:21:05Z | [0779fdb](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/0779fdbbfd6b2dd2ef0f5aa277e077f599d7b180) | Add annual KPI v3 parser and FY2024-25 tyre PDF fallback |
| 63 | 2026-09-05T14:21:30Z | [1676d9e](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/1676d9e9039caeab14131ef086fbe15b7bbb7743) | Add PDF parser for FY2024-25 tyre booklet fallback |
| 64 | 2026-09-05T14:21:43Z | [7808749](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/780874996fc72300d79e6614b71ffe59fea66afe) | Run Annual KPI v3 repair parser |
| 65 | 2026-09-05T16:41:21Z | [83f9c4e](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/83f9c4e3d2e9520a62dcdce6a66b59e2b279375b) | Harden annual product engine rows and clear stale dashboard rows |
| 66 | 2026-09-05T16:41:30Z | [27682df](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/27682df3817a2ea52a04ef53b93dae4819089874) | Run Annual KPI v4 strict dimension cleanup |
| 67 | 2026-09-05T16:45:26Z | [7606467](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/7606467e7249aef991026182507286de439e5e9e) | Fix LUB dt payload and add annual KPI serial number column |
| 68 | 2026-09-05T16:53:17Z | [3ba0640](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/3ba064074f7d777c8a3d1a4380d61009f6eb3845) | Restore annual history, enforce decimals, and fix LUB dt handling |
| 69 | 2026-09-05T16:53:27Z | [43d0bbf](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/43d0bbf0b7518d5c9009d2a40ab079a346fa9ff7) | Run Annual KPI v5 history repair |
| 70 | 2026-09-06T07:40:43Z | [fa866c5](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/fa866c55db3b55b7fcfa47f7b31ba49e507d7d18) | Use exact FY2024-25 tyre PDF depot codes and preserve source units |
| 71 | 2026-09-06T07:40:54Z | [48cb00d](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/48cb00d2b098bcc139ca370d85dd5db9c01e57d0) | Run Annual KPI v6 tyre PDF parser |
| 72 | 2026-09-06T07:46:42Z | [7f9929a](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/7f9929a653e6889a18f74b11e7d2f3408f7e6ba6) | Add Target column with source-only HSD and tyre targets |
| 73 | 2026-09-06T07:47:01Z | [91184b4](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/91184b4e5ef3c778efcb9fe34b5d29de54ee085f) | Run Annual KPI v7 with Target column |
| 74 | 2026-09-06T07:55:13Z | [d838436](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/d8384366ab53facd1b0fbe028d0a731147b13632) | Add BD MED and Spring KPI targets from exact depot source rows |
| 75 | 2026-09-06T08:01:28Z | [c4b73ad](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/c4b73ad2c7c1c8cb16d8261deeb9e3e934002db7) | Fix depot-wise Total Lub parser and keep FY targets from April |
| 76 | 2026-09-06T08:03:30Z | [0f982ac](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/0f982ac0911180aecad5fbfc7bd93c47ff6a4baf) | Add focused annual KPI source diagnostics |
| 77 | 2026-09-06T08:03:42Z | [b594cf8](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/b594cf80bb3b5eb1a2a6b5f7942f2351d1a4e5f9) | Add focused annual KPI diagnostic workflow |
| 78 | 2026-09-06T10:25:18Z | [58fe37e](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/58fe37e285b02373b63b2d50b08ba51591a22ad8) | Fix v8 meta hook import for diagnostics |
| 79 | 2026-09-06T10:33:44Z | [9c84f38](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/9c84f388812208ee8addb0143d3d660fea9f4954) | Fix LUB diagnostic to use v8 depot-wise parser |
| 80 | 2026-09-06T10:47:03Z | [8314b3c](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/8314b3c720b76ba6406ab5a821363928d9ebac2b) | Fix April target parsing and verified LUB form submission |
| 81 | 2026-09-06T10:47:21Z | [df82e8c](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/df82e8ca9b747470e563e3618eeeefcdabefeaea) | Expand annual diagnostics for LUB history and April targets |
| 82 | 2026-09-06T13:33:38Z | [180871f](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/180871f25843199ebf8ee41556cc1648e6ead7a0) | Add focused LUB browser-contract diagnostics |
| 83 | 2026-09-06T13:52:42Z | [7ddb7ac](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/7ddb7ac1b29fe472aae922e2c1b5b3baf08fb12e) | Test exact LUB yymm POST contract |
| 84 | 2026-09-06T14:01:56Z | [41762f8](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/41762f805486af84bb702f4301d0be78bf528cbb) | Fix v8 LUB with verified yymm POST contract |
| 85 | 2026-09-10T10:23:24Z | [de0bc93](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/de0bc93683ec66b3162288af732e26dde65de6e4) | Run Annual KPI production with v8 |
| 86 | 2026-09-10T10:33:12Z | [aaed69d](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/aaed69d4d051b9b61061a5dfb7723ad779ac3eec) | Add safe annual KPI v9 wrapper |
| 87 | 2026-09-10T10:33:27Z | [6c7286b](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/6c7286b45dbfc62e1f819418e68f0278650000db) | Run Annual KPI with safe v9 wrapper |
| 88 | 2026-09-10T12:48:36Z | [8456619](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/8456619e61ff17fe848a05566ff232a3817d4c6d) | Add safe annual backfill and fix tyre recursion |
| 89 | 2026-09-10T12:48:56Z | [4b1370b](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/4b1370bfb6f20601d2e3a1d6e27f1ed78b6a9a9f) | Run Annual KPI with v10 safe backfill |
| 90 | 2026-09-10T13:59:58Z | [d933fdc](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/d933fdca9516b180fa4c72a993631fe9fd3eb7d5) | Lock FY2024-25 unavailable-source exceptions |
| 91 | 2026-09-10T14:18:30Z | [3280141](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/32801411b1eef807bdd5a6d3fd0f26827a8476d8) | Retry transient Google Sheets timeouts in annual formatting |
| 92 | 2026-09-10T15:56:37Z | [4ea383a](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/4ea383af1005e0deb1202b7096a7f60b9a4b185f) | Add Annual Upto column borders |
| 93 | 2026-09-10T15:56:52Z | [f8ae62a](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/f8ae62af380c340797f019b9d6ec1c143c3a4e2b) | Use Annual v11 with Upto borders |
| 94 | 2026-09-10T16:59:26Z | [986b3a8](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/986b3a8195b1d0288e289193d935dd65d6d2738d) | Shift daily scheduler off GitHub Actions peak cron minute |
| 95 | 2026-09-14T06:56:43Z | [c6c1d53](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/c6c1d5385e349be032c37d7ada658b71a1715695) | Add APSRTC Report Automation app home page |
| 96 | 2026-09-14T06:56:59Z | [8dacd2e](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/8dacd2e9ca7b5a614881d6ea1d9b8ae87a74bd27) | Add APSRTC Report Automation privacy policy |
| 97 | 2026-09-17T04:40:52Z | [4c812d4](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/4c812d4202dcd619a7fc95f7f6101b6b83ba8924) | Add Drive helper to download prior monthly workbook |
| 98 | 2026-09-17T04:41:50Z | [b4e96ed](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/b4e96ed38063248e2d3cb31c87a9e075bd51a34e) | Add incremental vehicle history and schedule maintenance reporting |
| 99 | 2026-09-17T04:42:45Z | [28d9179](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/28d917983877bdaa4f7c28f14f562da154fbc7a9) | Build two-sheet incremental monthly vehicle performance workbook |
| 100 | 2026-09-17T17:06:33Z | [d30271a](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/d30271add4edea0f864cdc0959afee94d195a7e4) | Add controlled monthly vehicle history source validation |
| 101 | 2026-09-17T17:06:41Z | [224ab92](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/224ab9211e01b52c7ec2cc8e082d89abbddf372f) | Add manual Monthly source validation workflow |
| 102 | 2026-09-17T17:33:56Z | [84191b1](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/84191b1823220bf03479be9432de097badb5cc42) | Improve Monthly KMPL sorting and presentation |
| 103 | 2026-09-17T17:34:33Z | [231ca71](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/231ca710a3fa9593a9386ec88e727b2f779af976) | Group Vehicle Performance and improve visual layout |
| 104 | 2026-09-18T04:15:17Z | [1c68e96](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/1c68e969e010a5c55c6c17077a68c3886a852af3) | Add daily Schedule III/IV markers to Monthly KMPL |
| 105 | 2026-09-18T15:50:00Z | [9b7cd94](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/9b7cd941cb09a5fbeb08af59cc830a86668c4615) | Add safe Telegram chat ID retrieval workflow |
| 106 | 2026-09-18T16:11:35Z | [3979d2a](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/3979d2a7cac0de6b4f12c87783ecc72c22e2bacc) | Add Telegram notification test workflow |
| 107 | 2026-09-18T16:37:27Z | [91228c6](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/91228c6d1b99e3b942ff35eed0b28194751d7135) | Add Telegram notifications to Daily report workflow |
| 108 | 2026-09-18T16:57:00Z | [0653186](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/0653186de7f2ad5ecba24adb6991d0b5fdc2d69a) | Send full Daily report content to Telegram |
| 109 | 2026-09-18T17:03:35Z | [fb3d9bd](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/fb3d9bd43e0cb63f3f4270aceb0ade91d18e48b1) | Add reusable Telegram Daily report delivery |
| 110 | 2026-09-18T17:03:46Z | [0d79665](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/0d7966570cebb0ec59512f31b93278c905bc3e8c) | Deliver Google Form Daily reports to Telegram |
| 111 | 2026-09-18T17:06:35Z | [3e672e8](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/3e672e8e8d94945a4814fbfde39bdaed0ba080b1) | Integrate Telegram into Daily Google Form poller |
| 112 | 2026-09-18T17:11:14Z | [fc1146f](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/fc1146f951dde9949da394ec8656a6f544e04bc2) | Clarify Daily Form dispatch to GitHub Actions |
| 113 | 2026-09-18T17:17:19Z | [5cc5441](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/5cc5441cfe6fe4ea61fcab19f00638e0f995a7a7) | Allow Daily workflow to download existing Drive report |
| 114 | 2026-09-18T17:17:23Z | [7a0a233](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/7a0a23331efed63cb128111515af3e44bbe83ce2) | Recover existing Daily text for Telegram delivery |
| 115 | 2026-09-18T17:20:44Z | [c9e8770](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/c9e877071665b1e3b3e36d2685986a4aca169dcd) | Prevent duplicate Telegram messages on Daily schedule retries |
| 116 | 2026-09-19T05:53:55Z | [ccde079](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/ccde079715304f18d8c9e6a17ae31445c58ecb27) | Add professional Monthly report title hierarchy |
| 117 | 2026-09-19T05:54:07Z | [1fef8ea](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/1fef8eac85ed7dc4d380d1e8237e1d03b31eac66) | Give Vehicle Performance a professional report identity |
| 118 | 2026-09-19T05:56:07Z | [b8c3649](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/b8c3649a249069f6d03bc4d605c2d53f9cf3cce1) | Refine Vehicle Performance visual grouping and current FY emphasis |
| 119 | 2026-09-19T05:56:20Z | [445b5ee](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/445b5eeeffb854c27365904573e247f8d7e7ba6c) | Polish Monthly KMPL decision-focused formatting |
| 120 | 2026-09-19T07:05:40Z | [4640b07](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/4640b07643ff446f9cec0322caf10625e72c8309) | Add canonical Daily Vehicle Event Register model |
| 121 | 2026-09-19T07:05:53Z | [fa2885e](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/fa2885e272686f93c49c8a033ca1f6cae4a942f7) | Document Daily Vehicle Event Register architecture |
| 122 | 2026-09-19T08:55:19Z | [a0136ac](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/a0136aca1011244fc8726c9ea074af6b49f4b939) | Keep Annual v11 formatting patch on v10 layout contract |
| 123 | 2026-09-19T08:55:44Z | [acf89b0](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/acf89b0a739bd34f5de41db820a5926195a6ed25) | Add Vehicle 360 workbook summary builder |
| 124 | 2026-09-19T08:55:52Z | [3831665](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/3831665525a92ba8d6d934e4abf19e66aea099ec) | Include Vehicle 360 sheet in Monthly workbook |
| 125 | 2026-09-19T08:58:27Z | [02580be](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/02580beeb41b342b3b51eadf20ab6ad7f8790c58) | Add professional Annual KPI workbook presentation |
| 126 | 2026-09-19T09:37:33Z | [954e861](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/954e861f113b8ebcc7efed9f5e872455a7144feb) | Add normalized Event Register ingestion helpers |
| 127 | 2026-09-19T09:37:44Z | [d5c7ad2](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/d5c7ad2cad1bf7316913dbf66a728e759c087d9a) | Add Vehicle Event trigger entry point |
| 128 | 2026-09-19T09:37:54Z | [0070c66](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/0070c66a8b01395408b265e05b15975f32bd3dff) | Add manual Vehicle Event validation workflow |
| 129 | 2026-09-19T09:40:01Z | [8d06500](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/8d065002f16e90c8aee1e279b7e186068ca8b192) | Add Google Form trigger for Vehicle Event Register |
| 130 | 2026-09-20T03:16:47Z | [a57a4ad](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/a57a4ad671d24d8a65309478e30d076db6bf7530) | Harden Daily IST retry schedule |
| 131 | 2026-09-20T14:24:20Z | [ceba95b](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/ceba95b6245a8028ec93f53b39a653da059de6f2) | Align vehicle event model with live Form register |
| 132 | 2026-09-20T14:24:30Z | [fc68dc9](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/fc68dc9c015f2894cc06591a392d90452cee34a6) | Show structured breakdown and tyre history in Vehicle 360 |
| 133 | 2026-09-20T14:24:47Z | [f074842](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/f074842d0fbfde6808bcb67370961e4e7103dbb2) | Expand vehicle event workflow for live register fields |
| 134 | 2026-09-20T15:35:10Z | [d036637](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/d036637d8b86b704e2f5843787feea0f7f07feb9) | Productionize vehicle event Apps Script dispatch |
| 135 | 2026-09-20T16:22:29Z | [2eafd9c](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/2eafd9c7292e5f53c1c8602d58143db605614036) | Normalize APSRTC vehicle numbers consistently |
| 136 | 2026-09-20T16:22:46Z | [b6e5465](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/b6e54655a359c38e7d344fc204c705ce6a8ea351) | Normalize APSRTC vehicle numbers consistently |
| 137 | 2026-09-20T16:22:50Z | [b64a23c](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/b64a23c2e3ff851cb03d2680982058d133886291) | Normalize APSRTC vehicle numbers consistently |
| 138 | 2026-09-20T16:33:31Z | [59d4caf](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/59d4caf447c6d7d634b5263cda4dc0e76863fa1a) | Add secured read-only Vehicle Events API for Vehicle 360 |
| 139 | 2026-09-20T16:33:44Z | [0bf89b8](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/0bf89b83a60ec052e724751cbbbc63eda17d517e) | Fix vehicle whitespace normalization regex |
| 140 | 2026-09-20T17:45:50Z | [7725422](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/77254220e15f16f2cf2ae7188605a7390c06dc3f) | Read Vehicle 360 events from secured Apps Script API |
| 141 | 2026-09-20T17:45:56Z | [291c11e](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/291c11efbc97922670acc7d9b61611b9d8a80b82) | Connect permanent Vehicle Events to Vehicle 360 monthly sheet |
| 142 | 2026-09-20T17:46:01Z | [cdba069](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/cdba069d31b9c97ce02ee10475c0fcda172c3dcb) | Pass Vehicle Events API secrets to monthly report |
| 143 | 2026-09-21T03:41:15Z | [2339bb2](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/2339bb28d6e89e5dcfeaa6a7090195afa711fba0) | Fix Vehicle Events API parsing and vehicle normalization |
| 144 | 2026-09-21T03:41:17Z | [fca2558](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/fca25581c5736ee18d70460e09155891000af56a) | Add read-only Vehicle Events API health check |
| 145 | 2026-09-21T04:43:45Z | [883108c](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/883108c997c88dbfeb1f018cb7ce1a6200ee66db) | Accept Google display date formats in Vehicle Events API |
| 146 | 2026-09-21T05:30:36Z | [6c5aa0b](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/6c5aa0b802e724d40562e8f1f7969420ca6a7dd1) | Support provisional open-month vehicle roster |
| 147 | 2026-09-21T05:30:50Z | [496d603](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/496d603e02adf199c6a2276f9fe598316df2178d) | Implement open-month Vehicle 360 business lifecycle |
| 148 | 2026-09-21T05:37:30Z | [63f2604](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/63f2604e6a37a2f26269e2b5c505b4d081d32295) | Sync self-contained Vehicle Events API with deployed web app |
| 149 | 2026-09-21T05:40:28Z | [2551349](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/2551349e835098871c98ab9367049779c0bfef20) | Preserve recorded event status when GitHub dispatch fails |
| 150 | 2026-09-21T05:45:49Z | [9ddd66a](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/9ddd66ada780037e1801e4fa5811d419a6eb90e0) | Reject future months in Annual KPI form trigger |
| 151 | 2026-09-21T05:54:08Z | [be7eec8](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/be7eec871755f79a6b81f191b0753605370cd350) | Use exact normalized form field matching |
| 152 | 2026-09-21T05:54:14Z | [ac0bcdd](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/ac0bcdda36a98f1e1539022ca05c68b91352b181) | Use exact normalized form field matching |
| 153 | 2026-09-21T05:54:18Z | [dec3ccc](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/dec3ccca358a0229fb2d1be2b534ea33fd4b6538) | Use exact normalized form field matching |
| 154 | 2026-09-21T09:00:54Z | [5066953](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/50669530c3e16a7442a99df674ac4a3fcd4348b7) | Fix vehicle normalization and support open-month population label |
| 155 | 2026-09-21T09:01:05Z | [36e3cc9](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/36e3cc9c745c1a12d5a8b7f16321cbf9bb02f0ef) | Label open-month Vehicle Performance population as provisional |
| 156 | 2026-09-21T09:06:59Z | [c73eab0](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/c73eab096b8b24621acea4f00a1ea6710f3fcab5) | Separate open-month roster logic from finalized MTD-598 |
| 157 | 2026-09-21T09:07:14Z | [5305696](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/5305696f5c0dfc336d6d9e4c6eb3efa08e905962) | Make current-month reporting explicitly bypass MTD-598 |
| 158 | 2026-09-21T09:35:19Z | [ba8d7c8](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/ba8d7c8fb678ae19e06cc90cc55f1f4d047ce9a3) | Harden finalized-month MTD-598 vehicle parsing |
| 159 | 2026-09-21T09:35:46Z | [c00859c](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/c00859c31a7cc3c0beff0ed144a7beb93cefb9da) | Support operational KMPL coverage in open-month Vehicle 360 |
| 160 | 2026-09-21T09:36:01Z | [3c08bf7](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/3c08bf7367fcfa17d657e47db74a97172fed5e2e) | Differentiate open and closed month Vehicle 360 coverage |
| 161 | 2026-09-21T10:04:14Z | [93d2840](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/93d28407b8d6922ea33fcf3291d2b2efc43c9159) | Refresh existing monthly Google Sheet content on rerun |
| 162 | 2026-09-21T10:20:58Z | [d6f261b](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/d6f261bf7362bb5b26b0799a6c76614d04df9661) | Improve Vehicle 360 event readability with adaptive row heights |
| 163 | 2026-09-21T10:27:31Z | [2fbe760](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/2fbe7601e0904ce916467dda928d336699d48aa1) | Add authorized Telegram report command processor |
| 164 | 2026-09-21T10:27:37Z | [8238307](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/8238307fb2daa96d199634c0f34032f6da68ea14) | Add scheduled Telegram inbound command workflow |
| 165 | 2026-09-21T10:35:51Z | [9b03bb9](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/9b03bb9006c14576532923fffa619f175287ff4d) | Require depot explicitly for Telegram report commands |
| 166 | 2026-09-21T10:40:29Z | [2856879](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/2856879fd459f3b88e6809906424c0478f3c3337) | Add Telegram inline depot and report selection menus |
| 167 | 2026-09-21T10:42:50Z | [d5462ec](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/d5462ec468fcf9c0812d5eb33abe726b414952ed) | Add Telegram write API for permanent Vehicle Event register |
| 168 | 2026-09-21T10:43:25Z | [bd6df6d](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/bd6df6daca55e3cdd9eabae01e99159db8276eac) | Add guided Telegram Vehicle Event entry and confirmation |
| 169 | 2026-09-21T10:43:39Z | [564f3ee](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/564f3ee658d0572ddcc814fa9fe49bd0b6bf6b7c) | Connect Telegram bot to Vehicle Events permanent API |
| 170 | 2026-09-21T11:25:12Z | [5dcaae0](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/5dcaae09a8ba5048e4a34cb543d0059bc2107a79) | Allow all configured APSRTC depots in Vehicle Event API |
| 171 | 2026-09-21T11:25:37Z | [755e5fc](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/755e5fcc0d792111e6aaa7e0f00b1ace2972ffe1) | Use central depot master for Telegram menus |
| 172 | 2026-09-21T11:26:00Z | [5f1db78](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/5f1db7869aec54dc269b1228f98a122e4aee02ed) | Supply central depot master to Telegram bot |
| 173 | 2026-09-21T11:40:58Z | [652f625](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/652f62591ee7253413c5b211902f799b0a97578a) | Add Depot Master import and Vehicle Event Form sync |
| 174 | 2026-09-21T11:49:23Z | [201caff](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/201caff2bbebe7ade717dc5c20c6e8c155a57612) | Add professional Depot Master formatting |
| 175 | 2026-09-21T12:27:21Z | [a8a30db](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/a8a30db8b5e458504f1c5b15e31f3b4575ff38fa) | Add unified APSRTC Automation Hub dispatcher |
| 176 | 2026-09-21T12:32:14Z | [1da30fd](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/1da30fd36cddb3a4b0ac4102875d3b5a7461b694) | Add one-click APSRTC Automation Hub Form builder |
| 177 | 2026-09-21T12:45:54Z | [8171e4a](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/8171e4acca92ce1cdac0b1dbe902f1917d743ba7) | Refine Hub flow to select depot before service |
| 178 | 2026-09-21T12:54:54Z | [0fa7a8b](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/0fa7a8bf4defc3db002fcbe67cd8e38944ea06aa) | Add in-place professional Hub upgrade |
| 179 | 2026-09-21T13:02:38Z | [f41a659](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/f41a65954560052ab61ccb6853fb72a44f35fc90) | Fix in-place Hub item deletion |
| 180 | 2026-09-21T13:07:36Z | [6e62fc4](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/6e62fc4a9cf5b18e57a4d41d4eafb2d4090b5822) | Clear Form navigation before Hub rebuild |
| 181 | 2026-09-21T13:11:53Z | [cc4036a](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/cc4036afd7d97094787147b4b605e0620971c146) | Use non-destructive upgrade for branched Hub Form |
| 182 | 2026-09-21T13:13:23Z | [a177627](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/a1776278a0576b602076ef0a48d4fd46bda7bb48) | Fix FormApp moveItem index signature |
| 183 | 2026-09-21T13:23:08Z | [d2b8e35](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/d2b8e358c42351869d96388335e014040a766ac8) | Fix Hub item positioning without unsupported getItemIndex |
| 184 | 2026-09-21T13:53:12Z | [6c82a13](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/6c82a13da1ff7cc665206e48f4210a7c6205e60c) | Add clean APSRTC Automation Hub V2 builder |
| 185 | 2026-09-21T14:00:15Z | [cc68c3a](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/cc68c3af6ed14474bed878d5bab12ea24131dc6a) | Connect Hub V2 reports and permanent Vehicle Events |
| 186 | 2026-09-21T14:00:34Z | [0347b75](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/0347b751dd644c42a7f07853c9c5677bf003673d) | Make Vehicle Event IDs collision-safe across depots |
| 187 | 2026-09-21T14:30:26Z | [d539cf7](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/d539cf76315d138bb3f2b173e70674c787b71826) | Fix Hub Google Form US-locale date parsing |
| 188 | 2026-09-21T14:46:02Z | [ab7ae41](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/ab7ae417a3c9fd4b4ab48a5587c16e81a03b7f0a) | Accept Google Form date values for Hub monthly routing |
| 189 | 2026-09-21T14:58:40Z | [19c639c](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/19c639cbb2858892f36c53fd7f36eb322e9afd7f) | Add Telegram status notifications to monthly reports |
| 190 | 2026-09-21T14:58:57Z | [420de3e](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/420de3ed3c5eebb7b59a8a9f81cd685a2dd7252a) | Use selected depot in monthly report presentation |
| 191 | 2026-09-21T17:12:44Z | [017e9c7](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/017e9c7d4228af9a5bc2e3551b1dfe385ab1a185) | Prevent synthetic blank rows in Vehicle Performance history |
| 192 | 2026-09-21T17:14:52Z | [fb4e3c6](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/fb4e3c619f86a1d90b421013f5cc5fc43d4289a5) | Add depot identity and print-ready monthly history sheets |
| 193 | 2026-09-21T17:15:20Z | [b6ae381](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/b6ae3819f9bf6beba7e38b1b8d0a04476448309d) | Finalize print setup for monthly history sheets |
| 194 | 2026-09-21T17:15:36Z | [be6457b](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/be6457b6e76d72c142caeedd1c4236dcb42c8293) | Pass depot and period into monthly report sheets |
| 195 | 2026-09-21T17:24:09Z | [cdb36f4](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/cdb36f4a0cb0ffed8d283c2155e997e23e3746db) | Include Google Drive link in monthly Telegram status |
| 196 | 2026-09-21T17:26:36Z | [5028f35](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/5028f356248b77fd1cd9f173e54385003145b3a9) | Add Annual KPI Telegram status and Drive link |
| 197 | 2026-09-21T17:31:10Z | [75c0453](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/75c0453eaeb89bca43d42cac7bbfea000a010dbc) | Fix Annual KPI v11 Python syntax corruption |
| 198 | 2026-09-21T17:31:29Z | [ab6e681](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/ab6e6817c108db93903377c92afb76cde10dc553) | Add Drive Report Link column support to Automation Hub |
| 199 | 2026-09-21T17:44:44Z | [4c6b6a5](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/4c6b6a5b96bf47a6f4b3a4d2d1f5676303e7386c) | Prevent Annual KPI merge across frozen row boundary |
| 200 | 2026-09-21T18:08:59Z | [2ad4a42](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/2ad4a420a2f3f400ca8afae109cbc70e21d4b8ff) | Add approved two-sheet Annual KPI dashboard design |
| 201 | 2026-09-21T18:17:02Z | [4aa753e](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/4aa753e54330017751fc36546dea94e1d0e64b09) | Create live two-tab Annual KPI dashboard with variable current FY |
| 202 | 2026-09-21T18:30:05Z | [2f2a788](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/2f2a7885070598d0c9ec933efbae21c7b0a2e51f) | Clear Annual row and column freezes before merged-block rebuild |
| 203 | 2026-09-22T02:16:50Z | [50689a6](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/50689a67d2ef8884b2a2287c56802edfe3ede7a6) | Remove invalid four-column freeze from live Annual KPI sheet |
| 204 | 2026-09-22T02:39:29Z | [d9a4c30](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/d9a4c300d8faf01688e9408e0509f6f590d5df04) | Fix Annual KPI freeze at legacy formatter source |
| 205 | 2026-09-22T02:51:46Z | [24f0389](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/24f0389e5b8fb5894165ccda4d2e34c436a70462) | Fix Annual dashboard post-build os import |
| 206 | 2026-09-22T03:15:49Z | [e068fee](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/e068fee12a5d7615965e74f0accc9db670a7a3c5) | Accept Google Sheets URL as Annual report link |
| 207 | 2026-09-22T03:38:53Z | [cf53a78](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/cf53a7815c30ce6f2559417391402e6fc8678b90) | Clean legacy merges and add FY banding to Annual detail |
| 208 | 2026-09-22T03:39:10Z | [0b148ee](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/0b148ee32830cb1369f08a827f48e3389caf89a4) | Populate all three FY values in live Annual dashboard |
| 209 | 2026-09-22T04:06:30Z | [88018b4](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/88018b49b7e086a8d6f424736011287f7652bd2c) | Polish live Annual KPI executive dashboard and add 3-FY chart |
| 210 | 2026-09-22T05:53:33Z | [732817d](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/732817dc4102af61f8be17c142ecb265d9810a1e) | Wire Automation Hub report-link callback endpoint |
| 211 | 2026-09-22T05:53:53Z | [5d2b287](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/5d2b28773a2603e622c9156cff664b018cc1c35b) | Return Annual Google Sheet link to Automation Hub register |
| 212 | 2026-09-22T06:27:58Z | [c788dcd](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/c788dcdfc6b861181540b1884acb1291278e31f3) | Fix Annual dashboard chart Python syntax |
| 213 | 2026-09-22T06:37:53Z | [29a1080](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/29a10801ff80112b6152b9f4aa96419f5959ce1b) | Fix Annual KPI FY banding syntax |
| 214 | 2026-09-22T07:11:40Z | [39a6ab4](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/39a6ab48a0f8d543a6352b74f9861824e8a1f7eb) | Validate Annual runner syntax before production execution |
| 215 | 2026-09-22T07:13:57Z | [a0f9cf1](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/a0f9cf137f5a7352e905f50cde11257346a7f6d9) | Harden Annual KPI Google Sheets formatting requests |
| 216 | 2026-09-22T08:52:17Z | [eaf0ae1](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/eaf0ae14ea0350482e9820e18aa4e2a3ca63109c) | Fix Annual KPI two-sheet output and Sheets formatting |
| 217 | 2026-09-22T08:52:32Z | [312d4f4](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/312d4f40d5bb6800019c4499cfbe839c1e21797c) | Fail Annual workflow when generator fails |
| 218 | 2026-09-22T08:53:11Z | [732dfae](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/732dfae583437b64e4055ccce42f87028a153e66) | Prevent Hub report month timezone shift |
| 219 | 2026-09-22T10:06:33Z | [ea7db46](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/ea7db46014d191d4096408b479a78e8fb5409552) | Avoid dashboard freeze boundary across merged header |
| 220 | 2026-09-22T10:09:21Z | [cda251f](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/cda251f91c6eb2d67d21430070fa7983401264ea) | Run one controlled Annual KPI verification on workflow update |
| 221 | 2026-09-22T10:12:38Z | [f10c73f](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/f10c73fdc66e5c399be316e0993b6fa7aebcf87a) | Carry KPI labels across Annual dashboard FY rows |
| 222 | 2026-09-22T10:12:47Z | [9f1b644](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/9f1b644433df515f63fdcb5e85e4cc7dd4f63282) | Run final Annual KPI dashboard verification |
| 223 | 2026-09-22T10:15:19Z | [55820a6](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/55820a69531f4a90198a787ea7cc70a5b3443f6a) | Restore Annual KPI workflow to dispatch-only production mode |
| 224 | 2026-09-22T10:38:11Z | [d5862b5](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/d5862b5fbbbde79f88a91e6cec573a0fd9d0b81a) | Use date-effective Rajampet tyre district routing |
| 225 | 2026-09-22T10:43:02Z | [ce4f255](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/ce4f2552df777fc09ec7d2218d012c6e66157a41) | Polish Annual KPI live workbook and dashboard |
| 226 | 2026-09-22T10:43:30Z | [074838d](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/074838d361a6d962bb8632bf222f728581ddbf80) | Run controlled RAJAMPET June 2026 Annual KPI validation |
| 227 | 2026-09-22T23:50:01Z | [794adb0](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/794adb0dd550d2a9bef324eb19cae0d60f963ba3) | Fix Annual KPI live detail formatting service |
| 228 | 2026-09-22T23:50:10Z | [73c2cd8](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/73c2cd8db251cb9e79a78538a334cc95f6837f97) | Retry professional Annual KPI validation |
| 229 | 2026-09-22T23:53:57Z | [ce7ce45](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/ce7ce45b662cbbe7bf9d17732e72de82b3499f53) | Use historical RJPT tyre identity before Jan 2026 |
| 230 | 2026-09-22T23:54:10Z | [7b17bb0](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/7b17bb08e7ded5ef8937d4a5a4cc709d20573338) | Reject empty tyre backfill results |
| 231 | 2026-09-22T23:54:25Z | [58f3a93](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/58f3a93a991f5c768c275c2f1d7488ab97b93b8b) | Validate historical RAJAMPET tyre routing |
| 232 | 2026-09-23T00:04:43Z | [e7525ef](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/e7525ef5f495543fb91ea4090611222eb73cec0d) | Auto-resolve historical RAJAMPET tyre portal route |
| 233 | 2026-09-23T00:04:51Z | [e9d9d73](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/e9d9d731a627a1d40c9fd0cf3b30e8e330b14623) | Validate historical tyre route discovery |
| 234 | 2026-09-23T00:08:25Z | [b7b22c7](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/b7b22c79d1ebcdb2d3be93b0ff631253356a9afe) | Restore Annual KPI workflow to dispatch-only mode |
| 235 | 2026-09-23T00:20:56Z | [20ce30e](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/20ce30ef92adfe92cfe8a69a9ff687333faf4a31) | Fetch tyre KPIs by depot across all zones and regions |
| 236 | 2026-09-23T00:21:11Z | [c095b12](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/c095b123900f17ece3833518f02c5a99bf460cb6) | Validate depot-only tyre KPI lookup |
| 237 | 2026-09-23T00:30:12Z | [9c39dc9](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/9c39dc9ece010e2bf0893282924c97c689d1a845) | Restore Annual KPI workflow after depot-only tyre validation |
| 238 | 2026-09-23T16:23:00Z | [f205c41](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/f205c419aa890352d5016e9207e2e4d4726eccdb) | Improve annual KPI presentation and report print identity; repair Telegram event entry and add annual reports |
| 239 | 2026-09-23T16:38:06Z | [2676eb0](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/2676eb009632149585ef7ddc91768ab5373e88e3) | Preserve annual history and month-specific cumulative snapshots; fetch missing sources only; make Telegram depot-first |
| 240 | 2026-09-23T16:54:55Z | [a356424](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/a356424e49f252045f30e1b8687d50e4c5cd66a6) | Hide legacy annual spacer column and register verified Telegram commands |
| 241 | 2026-09-24T02:15:15Z | [d5e81a2](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/d5e81a26f02d00d40bf9988fe367e4faca4ac07d) | Add persistent Telegram listener service and explicit depot/date selection |
| 242 | 2026-09-24T06:58:03Z | [1d5e1d6](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/1d5e1d6afa31b7c68d6bf511266ecdaffafa1185) | Add Google Apps Script Telegram webhook |
| 243 | 2026-09-27T15:44:39Z | [e1d8570](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/e1d8570c4fb9d5c40866dcc98646cd267da31efc) | Repair legacy engine KPI history row sets |
| 244 | 2026-09-28T12:42:39Z | [2b8e530](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/2b8e5309034cdf6435bf1a9b8eb4592e8fa18704) | Make unavailable Annual KPI Upto values explicit |
| 245 | 2026-09-28T16:13:43Z | [24d2594](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/24d2594eb0e108b2eeed1f9db69486f5017e137c) | Fix Telegram default command registration |
| 246 | 2026-09-28T16:21:37Z | [07cc97d](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/07cc97d913b1e9631b4a5ff970db771cd17441b7) | Show Telegram API error details in configuration logs |
| 247 | 2026-09-28T16:46:49Z | [c8ae633](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/c8ae633e62c71cf25e3983792a56b597c971bbd5) | Fix Apps Script Telegram default command registration |
| 248 | 2026-09-28T16:47:35Z | [9ae584b](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/9ae584b6f2a9269fad388f2d8d22c19dc5c706ba) | Validate Telegram webhook URL and expose API errors |
| 249 | 2026-09-29T02:56:00Z | [28dd30f](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/28dd30f87fcb91e4cc63b29802ed1384dd268a85) | Improve Telegram input flow and suppress duplicate menus |
| 250 | 2026-09-29T03:13:34Z | [abcb184](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/abcb1845c9dc104fa9e3d5249266b19f529968c6) | Use GitHub token for GHCR image publishing |
| 251 | 2026-09-29T04:33:08Z | [25b41e2](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/25b41e217be4546b1df031da8c7dafec9a8d55f4) | Add explicit Telegram webhook execution logging |
| 252 | 2026-09-29T05:15:14Z | [e348128](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/e348128c71dae2c32ea6f34fb9447a9f4cfebc5f) | Persist webhook status for reliable diagnostics |
| 253 | 2026-09-29T05:43:29Z | [a68574e](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/a68574edf676f34e000b191c5bc1ef1d08f63c9d) | Show Telegram dispatch failures to the user |
| 254 | 2026-09-29T05:53:32Z | [eab9e83](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/eab9e830250f0529fb443dcd6cfd6bcc30290c5e) | Clean up Telegram menus after selections |
| 255 | 2026-09-29T05:54:06Z | [ad4b783](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/ad4b78356829c0c66faabc8a8bd23b184a6f05f4) | Improve Telegram report selection flow and date defaults |
| 256 | 2026-09-29T07:00:00Z | [eb2bbbb](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/eb2bbbb10eca5007481a815b22a21518d8297f3b) | Add guided report request flow with review and submit |
| 257 | 2026-09-29T07:00:19Z | [e686677](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/e686677c0c9179aeea02ce488b0612081b2b091f) | Provide safe depot fallback for polling bot |
| 258 | 2026-09-29T07:22:15Z | [5a0b569](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/5a0b569bbcac4f4688ad998fc9bd2b4620681bb8) | Acknowledge Telegram batches before processing |
| 259 | 2026-09-29T07:34:44Z | [2759d55](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/2759d558d747ae56640886cbb5dc686e49d17da8) | Add reliable one-minute Telegram polling trigger |
| 260 | 2026-09-29T07:48:48Z | [2815b50](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/2815b505feb5dab94cd02fdb0bda82ebc2e7cf88) | Add fast one-line report command path |
| 261 | 2026-09-29T07:52:39Z | [5b6428d](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/5b6428d8dd98744f077add16ebd154efa821facf) | Fix Apps Script duplicate command variable syntax error |
| 262 | 2026-09-29T08:24:45Z | [e5619ae](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/e5619ae7bd8ba2d9b0939563bb7a6bb759796dcf) | Fix one-line report command parsing |
| 263 | 2026-09-29T09:14:39Z | [d345460](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/d345460f18c8f87de0272ac9d4faae13b164b246) | Add guided depot prefix report flow |
| 264 | 2026-09-29T09:32:53Z | [7b0f544](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/7b0f5446a6bd8eb5629d5c48e57c029c54d07cce) | Expand tyre depot fallback while preserving portal and PDF codes |
| 265 | 2026-09-29T09:33:12Z | [d553752](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/d5537522d6a39713547b2ea3383dbed967ed099a) | Show both HSD KPIs on Annual dashboard cards |
| 266 | 2026-09-29T09:33:46Z | [d50a335](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/d50a3358012a485e20ae3e927da279ef70956710) | Allow exact FY24-25 tyre history backfill from official booklets |
| 267 | 2026-09-29T09:34:17Z | [4f5ce55](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/4f5ce55b033e85127d8c0f9f9fdf04c0b1979f94) | Cover FY24-25 tyre historical backfill behavior |
| 268 | 2026-09-29T09:35:55Z | [2b55416](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/2b55416d83e9c5132a632996ab1f6e830329bd4b) | Validate annual tyre adapter and dashboard modules in workflow |
| 269 | 2026-09-29T09:36:11Z | [6238308](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/623830897f89e35b3c9ae9dda1f9aadf9f68fb98) | Cover four-card Annual dashboard presentation |
| 270 | 2026-09-29T11:48:27Z | [46a4aaf](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/46a4aaf3412f9033a67aa31a03f9896abb2d0bd6) | Harden Annual print layout and chart legend labels |
| 271 | 2026-09-29T12:46:50Z | [ebb6f9f](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/ebb6f9f6977b59d8d44f5ee45779bc185aed3f08) | Harden Product and Engine Upto column parsing |
| 272 | 2026-09-29T13:59:22Z | [467e4b4](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/467e4b4cdd7f2f32c3557766bb5b58fa8ee70fb4) | Handle APSRTC multi-row Engine headers for Upto |
| 273 | 2026-09-29T14:15:24Z | [2f8c487](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/2f8c4872eec256459872be65a9c29393cb5493a5) | Repair truncated Annual parser module |
| 274 | 2026-09-29T14:33:04Z | [72ef9ec](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/72ef9ec2a69672854a5a8b4eb558aa4073cc8718) | Fix split-row APSRTC Engine header detection |
| 275 | 2026-09-29T15:23:08Z | [7e0b367](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/7e0b3676664a9d2383d4047ca4dda3c957ffa4b1) | Trace live Engine Upto parsing during annual repair |
| 276 | 2026-09-29T15:23:28Z | [1a43c1d](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/1a43c1d9c2c670f297f84648a9f3c01a89e492f2) | Upload Annual KPI diagnostic log |
| 277 | 2026-09-29T16:21:54Z | [55e029b](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/55e029bf70301c584c23b27680a69c82e4a541b8) | Add Proddatur Engine Upto source diagnostics |
| 278 | 2026-09-29T16:24:01Z | [693d73e](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/693d73e14a6c175112b7e4e6d1bfe3081688888f) | Probe alternate Engine report endpoints for legacy Upto values |
| 279 | 2026-09-29T16:25:55Z | [b437174](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/b43717451130fe94eac7ef06f69e7dcdc60b01b0) | Check legacy Engine rows across Proddatur region variants |
| 280 | 2026-09-29T16:27:59Z | [4b6fab9](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/4b6fab929a94bec2228770d84b070887378a14ba) | Check Engine source depot identifier variants |
| 281 | 2026-09-29T16:30:13Z | [f3268da](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/f3268dacd7cb58903d09fc0240ea6718857bceee) | Remove temporary Engine source probes after diagnosis |
| 282 | 2026-09-29T16:30:21Z | [017da65](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/017da654b3bc3926f38859043f621eee33e6e774) | Remove temporary Engine fetch trace after diagnosis |
| 283 | 2026-09-30T12:49:24Z | [ceaa3b8](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/ceaa3b80d18e49c2060a9c039d4bde842cf47507) | Fix monthly Hub dispatch contract and report-link callback |
| 284 | 2026-09-30T13:29:52Z | [32b04f1](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/32b04f13ce6aa47e4ad5539e3896d0dcf9768b58) | Accept daily Hub row and return manual report links; preserve scheduled reports |
| 285 | 2026-09-30T13:37:03Z | [d7a942e](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/d7a942e04e3639719fd75e44ddbb018c4b8958c0) | Embed official APSRTC branding and grade report performance without changing data |
| 286 | 2026-09-30T14:15:10Z | [698d231](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/698d23178dafacebbb59fc030f8c3c69fb1af3dc) | Merge pull request #2 from imranshaik-pro/fix/monthly-hub-dispatch |
| 287 | 2026-09-30T14:15:14Z | [1a8aef5](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/1a8aef58c0909c347b8d23d1cd6007a80136cdb9) | Merge pull request #3 from imranshaik-pro/fix/report-branding-performance-colours |
| 288 | 2026-10-02T03:06:51Z | [314f85d](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/314f85d04156d0b7a48af8dcb7580cc77c4fbdf4) | Fix daily KMPL slab counting and repair regression checks (#6) |
| 289 | 2026-10-02T03:07:46Z | [df13f60](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/df13f60458e56af52845b3222eb9159ee09dae7b) | Add current-request tyre checks and daily Telegram tables (#5) |
| 290 | 2026-10-02T03:11:45Z | [db2303a](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/db2303a5532233617b4fbde32001064329c1a217) | Record approved daily production release and verification [skip ci] |
| 291 | 2026-10-02T09:39:37Z | [d846501](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/d8465010eddd55d9a41c5dc4a70fb5e116ea9736) | Implement and lock approved daily-v1 report and Telegram formatting |
| 292 | 2026-10-02T09:48:47Z | [c84f00a](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/c84f00a0f07f4ff9a58880ec1d4b442a7552dbc4) | Keep complete daily Telegram reports within supported message size |
| 293 | 2026-10-02T09:55:19Z | [9185ac3](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/9185ac3655affa1d7ede84481b8b5e10d5729e1d) | Record successful locked daily template live verification [skip ci] |
| 294 | 2026-10-02T10:31:49Z | [a6d740c](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/a6d740cc391ea311dc6523a7ba5fbbb520cb0ee4) | Apply approved alignment and redundant tyre/KPI presentation corrections |
| 295 | 2026-10-02T11:01:46Z | [54dcf6b](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/54dcf6bd760bbf60d728ce1aee8677b54021b177) | Merge PR #7: approved daily-v1.1 report template |

For changes after this baseline, preserve the existing ledger and append newly reviewed commits, or regenerate against a new explicit baseline with full pagination. Never silently include unmerged proposals as production releases.

## Approved additions after the audited baseline

| No. | Commit date UTC | Commit | Change |
| --- | --- | --- | --- |
| 296 | 2026-10-02T19:34:19Z | [b342269](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/b342269b487e0c363b14238e349ee6c7194894a0) | Consolidate project rules, sources, flows and complete history; documentation-only PR #8 head |
| 297 | 2026-10-02T19:41:01Z | [cf07f0f](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/cf07f0ff163b1af7d88e18cf671e7f61ec5bddcc) | Merge owner-approved documentation PR #8; production base for the detail-tabs review |

## Detail-tabs development and approved release

These commits were developed and verified on [PR #9](https://github.com/imranshaik-pro/apsrtc-kmpl/pull/9). The owner approved production on 3 October 2026 with count-only FY Total rows; PR merge metadata records the release commit.

| Commit | Change |
| --- | --- |
| [41b3846](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/41b3846d3219b900cf7a3481a379238932505b92) | Capture authenticated engine/product UD and UM source contracts |
| [66c9a4c](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/66c9a4c6c9afa22f88c7d4cb0a28c74d454a22a9) | Add source-preserving Monthly and Annual detail tabs |
| [6b6e41f](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/6b6e41fd5e083dffb332d0cc9d9e1c3755652497) | Polish detail views, apply established KMPL colours and document UD/UM rules |
| [bb396c3](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/bb396c37c77f18220c694bd7f781835ab13bec0d) | Preserve Monthly's fresh-session lifecycle in previews and distinguish provisional tyre month data from daily cutoffs |
| [6afcdc3](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/6afcdc368d05dfddcaf51a9836451cf4a3f9f494) | Keep the FY25-26 history floor specific to Annual; validate standalone Monthly source selection |

| [b14ded9](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/b14ded93cf34154ceaae3838c5626389d6efc87c) | Record initial B/F source/workbook/native Sheets acceptance |
| [8e5e821](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/8e5e8216f337609f53b4530412fa893328c22b2a) | Apply owner tyre model, add Statement C, correct fiscal-year formulas, and preserve source discrepancies |

| [cb0ac0d](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/cb0ac0d9f77a238fc60220ce8b2d188f3bc722a9) | Align calculated tyre totals and clarify Monthly source heading |

| [838b71d](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/838b71dffbef7840e28ac57277c5fc61e3961749) | Record owner-template source/formula/workbook acceptance and documentation |
| [15c399c](https://github.com/imranshaik-pro/apsrtc-kmpl/commit/15c399c5dc2ee2257ccda0fe6ae44270f44c1b72) | Apply final owner rule: FY count SUMs only, blank percentage totals; validate before approved release |

The review's final documentation update records source/workbook/Sheets acceptance and the owner approval boundary. See [detail-tabs evidence](monthly-annual-detail-tabs.md).


## Post-baseline release addendum — 7 October 2026

The original numbered ledger above remains the historical 3 October baseline. Later production milestones relevant to the KMPL range work are:

| UTC date | Commit | Recorded change |
| --- | --- | --- |
| 2026-10-07 | `150555a55748090084d1eaa8da4a03adf0afa276` | Merge PR #12: source-backed Vehicle/Driver Month and Upto KMPL range reporting in Monthly and Annual KPI |
| 2026-10-07 | `fe4e2c212d9db68880fc4f0cf4199de95ffe3f21` | Ensure Month/Upto range tests run in direct unittest mode |
| 2026-10-07 | `92c3486add5ca87bff8cf1e31bd99946ffa52714` | Merge PR #14: harden Month/Upto KMPL range tests |

The PR #12 merge and PR #14 test follow-up supersede earlier open-branch descriptions of the range feature. Detailed source and validation conclusions are maintained in `kmpl-range-sheets.md` and `operations-and-validation.md`.
