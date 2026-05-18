# Data Dictionary

| Table | Grain | Purpose |
|---|---|---|
| `product_features.csv` | Product feature | Feature metadata, product area, device, service tier, owner, stage, and business question |
| `daily_feature_metrics.csv` | Date x feature x customer segment | Engagement, conversion, retention, playback quality, satisfaction proxy, and data quality metrics |
| `experiment_results.csv` | Experiment x segment x variant | Control and treatment results for A/B and multivariate tests |
| `metric_definitions.csv` | Metric | Metric meaning, role, source table, and owner |
| `data_quality_checks.csv` | Feature x quality check | Freshness, completeness, duplicate exposure, metric definition, and segment join checks |
| `stakeholder_requests.csv` | Request | Ad hoc business questions, requester type, decision needed, urgency, and status |
| `analysis/outputs/product_priority_queue.csv` | Product feature | Ranked feature recommendations with experiment lift, confidence, guardrail risk, and next move |
| `analysis/outputs/experiment_readouts.csv` | Experiment | Statistical readout, guardrail movement, segment heterogeneity, confidence, and decision |
| `analysis/outputs/segment_summary.csv` | Customer segment | Segment-level active accounts, watch minutes, conversion, and retention |
| `analysis/outputs/metric_trust_queue.csv` | Feature x quality check | Lowest-trust checks to fix before scaling reporting |
