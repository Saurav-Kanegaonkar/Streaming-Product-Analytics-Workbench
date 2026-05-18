import csv
import json
import math
import random
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ANALYSIS = ROOT / "analysis"
OUTPUTS = ANALYSIS / "outputs"
SRC = ROOT / "src"
SEED = 51726


def pct(value):
    return round(value, 4)


def rounded(value, digits=1):
    return round(value, digits)


def safe_div(numerator, denominator):
    return numerator / denominator if denominator else 0


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normal_cdf(value):
    return 0.5 * (1 + math.erf(value / math.sqrt(2)))


def two_prop_p_value(success_a, total_a, success_b, total_b):
    p_a = safe_div(success_a, total_a)
    p_b = safe_div(success_b, total_b)
    pooled = safe_div(success_a + success_b, total_a + total_b)
    se = math.sqrt(pooled * (1 - pooled) * (safe_div(1, total_a) + safe_div(1, total_b)))
    if se == 0:
        return 1.0
    z_score = (p_b - p_a) / se
    return 2 * (1 - normal_cdf(abs(z_score)))


def build():
    random.seed(SEED)
    DATA.mkdir(exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    SRC.mkdir(exist_ok=True)

    features = [
        ("F001", "Continue Watching Rail", "Home", "Connected TV", "SVOD", "Product", "launched", "Does resume placement increase completed plays?"),
        ("F002", "Personalized Top Picks", "Home", "Connected TV", "SVOD", "ML Product", "experiment", "Does ranking personalization increase qualified starts?"),
        ("F003", "Short Preview Autoplay", "Discovery", "Mobile", "SVOD", "Growth", "experiment", "Do previews improve title discovery without raising exits?"),
        ("F004", "Sports Live Hub", "Live", "Connected TV", "Ad Supported", "Live Product", "beta", "Does live event packaging improve return visits?"),
        ("F005", "Kids Profile Gate", "Profiles", "Tablet", "SVOD", "Trust", "launched", "Does safety friction preserve engagement while reducing support issues?"),
        ("F006", "Offline Downloads", "Playback", "Mobile", "SVOD", "Playback", "launched", "Which device segments benefit most from download reminders?"),
        ("F007", "Ad Load Balancer", "Ads", "Connected TV", "Ad Supported", "Ads Product", "experiment", "Can ad pod tuning improve completion without hurting watch time?"),
        ("F008", "Search Intent Rewrite", "Search", "Web", "SVOD", "Search", "experiment", "Does query rewrite raise successful search sessions?"),
        ("F009", "Household Switcher", "Profiles", "Connected TV", "SVOD", "Identity", "beta", "Does lower profile switching friction increase household usage?"),
        ("F010", "Watch Party Invite", "Social", "Mobile", "SVOD", "Growth", "concept", "Which cohorts respond to social viewing invitations?"),
        ("F011", "New Episode Reminder", "Notifications", "Mobile", "SVOD", "Lifecycle", "launched", "Do reminders lift day-seven retention for episodic viewers?"),
        ("F012", "FAST Channel Guide", "Live", "Web", "Ad Supported", "Live Product", "experiment", "Does a lean guide improve channel starts and ad completion?"),
    ]
    segments = {
        "Returning binge viewers": {"watch": 1.28, "retention": 0.35, "conversion": 0.26},
        "New trial households": {"watch": 0.72, "retention": 0.21, "conversion": 0.18},
        "Sports event viewers": {"watch": 1.06, "retention": 0.25, "conversion": 0.22},
        "Kids co-viewing households": {"watch": 0.92, "retention": 0.31, "conversion": 0.2},
        "Ad-supported explorers": {"watch": 0.84, "retention": 0.19, "conversion": 0.16},
    }
    device_mod = {
        "Connected TV": {"startup": 820, "rebuffer": 0.011, "crash": 0.002, "sessions": 1.18},
        "Mobile": {"startup": 630, "rebuffer": 0.015, "crash": 0.004, "sessions": 0.94},
        "Tablet": {"startup": 690, "rebuffer": 0.013, "crash": 0.003, "sessions": 0.76},
        "Web": {"startup": 590, "rebuffer": 0.009, "crash": 0.003, "sessions": 0.68},
    }
    feature_mod = {
        "Home": 1.22,
        "Discovery": 0.86,
        "Live": 1.04,
        "Profiles": 0.74,
        "Playback": 0.91,
        "Ads": 0.8,
        "Search": 0.7,
        "Social": 0.48,
        "Notifications": 0.66,
    }
    start = date(2026, 1, 1)
    days = 120

    feature_rows = []
    daily_rows = []
    quality_rows = []
    request_rows = []

    for feature_id, name, area, device, tier, owner, stage, question in features:
        feature_rows.append(
            {
                "feature_id": feature_id,
                "feature_name": name,
                "product_area": area,
                "primary_device": device,
                "service_tier": tier,
                "business_owner": owner,
                "launch_stage": stage,
                "business_question": question,
            }
        )

    for offset in range(days):
        current = start + timedelta(days=offset)
        weekday = current.weekday()
        weekend_factor = 1.18 if weekday in [4, 5, 6] else 0.94
        release_pulse = 1 + math.sin(offset / 9.5) * 0.055
        sports_pulse = 1.22 if offset in range(31, 42) or offset in range(82, 94) else 1
        for feature_id, name, area, device, tier, owner, stage, question in features:
            for segment, s_meta in segments.items():
                base_accounts = 8200 * feature_mod[area] * device_mod[device]["sessions"] * random.uniform(0.86, 1.16)
                if area == "Live" and segment == "Sports event viewers":
                    base_accounts *= sports_pulse * 1.42
                if area == "Kids Profile Gate" and segment != "Kids co-viewing households":
                    base_accounts *= 0.38
                active_accounts = max(350, int(base_accounts * weekend_factor * release_pulse))
                sessions = int(active_accounts * random.uniform(1.18, 2.45))
                starts = int(sessions * random.uniform(0.42, 0.72))
                conversion_rate = s_meta["conversion"] + random.uniform(-0.025, 0.035)
                retention_rate = s_meta["retention"] + random.uniform(-0.03, 0.025)
                search_success = 0.74 + random.uniform(-0.06, 0.07)
                if area == "Search":
                    search_success += random.uniform(0.04, 0.09)
                avg_watch_minutes = 31 * s_meta["watch"] * random.uniform(0.84, 1.18)
                rebuffer = device_mod[device]["rebuffer"] + random.uniform(-0.003, 0.007)
                startup = device_mod[device]["startup"] * random.uniform(0.84, 1.24)
                crash = device_mod[device]["crash"] + random.uniform(-0.001, 0.003)
                if feature_id == "F004" and offset in range(82, 94):
                    startup *= 1.18
                    rebuffer += 0.006
                if feature_id == "F007" and offset in range(51, 67):
                    avg_watch_minutes *= 0.94
                    rebuffer += 0.004
                if feature_id == "F008" and offset in range(70, 79):
                    search_success -= 0.08
                data_quality = 98.2 - random.uniform(0, 3.8)
                if feature_id in ["F004", "F007", "F008"] and offset in range(51, 79):
                    data_quality -= random.uniform(5, 12)
                if segment == "Ad-supported explorers" and feature_id == "F007":
                    data_quality -= random.uniform(2, 5)
                data_quality = max(68, min(99.4, data_quality))
                satisfaction = 72 + avg_watch_minutes * 0.18 + conversion_rate * 28 - startup / 115 - rebuffer * 220
                daily_rows.append(
                    {
                        "date": current.isoformat(),
                        "feature_id": feature_id,
                        "feature_name": name,
                        "product_area": area,
                        "device_family": device,
                        "service_tier": tier,
                        "customer_segment": segment,
                        "active_accounts": active_accounts,
                        "sessions": sessions,
                        "qualified_starts": starts,
                        "avg_watch_minutes": rounded(avg_watch_minutes, 2),
                        "conversion_rate": pct(max(0.07, min(0.48, conversion_rate))),
                        "day7_retention_rate": pct(max(0.08, min(0.54, retention_rate))),
                        "search_success_rate": pct(max(0.49, min(0.93, search_success))),
                        "playback_start_ms": int(startup),
                        "rebuffer_rate": pct(max(0.001, min(0.05, rebuffer))),
                        "crash_rate": pct(max(0.0004, min(0.018, crash))),
                        "satisfaction_proxy": rounded(max(42, min(93, satisfaction)), 1),
                        "data_quality_score": rounded(data_quality, 1),
                    }
                )

    check_types = [
        ("freshness", "Metric mart refresh finished before product standup"),
        ("completeness", "Event coverage reconciles to playback and exposure logs"),
        ("duplicate_exposure", "Experiment exposure table has one assignment per user"),
        ("metric_definition", "Certified metric definition exists for stakeholder use"),
        ("segment_join", "Account and device segment joins match expected coverage"),
    ]
    for feature_id, name, area, device, tier, owner, stage, question in features:
        for check_type, check_name in check_types:
            base = random.uniform(82, 99)
            if feature_id in ["F004", "F007", "F008"] and check_type in ["freshness", "duplicate_exposure", "segment_join"]:
                base -= random.uniform(9, 18)
            status = "pass" if base >= 90 else "watch" if base >= 80 else "fail"
            quality_rows.append(
                {
                    "check_id": f"DQ{len(quality_rows)+1:03d}",
                    "feature_id": feature_id,
                    "feature_name": name,
                    "check_type": check_type,
                    "check_name": check_name,
                    "score": rounded(max(58, min(99.5, base)), 1),
                    "status": status,
                    "owner": random.choice(["analytics engineering", "product analytics", "data platform", "experiment platform"]),
                    "recommended_fix": random.choice(["Backfill missing events", "Certify metric definition", "Add exposure dedupe test", "Refresh segment mapping", "Document lineage owner"]),
                }
            )

    request_topics = [
        "Why did connected TV completion drop after live hub launch?",
        "Which device segment should receive the next preview treatment?",
        "Can we ship ad load tuning without hurting watch time?",
        "Which search cohorts explain the recent successful search decline?",
        "Which retention movement is statistically reliable after reminders?",
        "Where should the next roadmap review focus for feature cleanup?",
    ]
    for index in range(30):
        feature = random.choice(features)
        request_rows.append(
            {
                "request_id": f"REQ{index+1:03d}",
                "opened_date": (start + timedelta(days=random.randint(15, days - 1))).isoformat(),
                "requester": random.choice(["product manager", "business lead", "engineering manager", "content strategy", "ad product lead"]),
                "feature_id": feature[0],
                "question": random.choice(request_topics),
                "decision_needed": random.choice(["launch decision", "roadmap priority", "root cause readout", "metric definition", "weekly business review"]),
                "urgency": random.choice(["high", "medium", "medium", "low"]),
                "status": random.choice(["answered", "in analysis", "queued", "needs data fix"]),
            }
        )

    metric_definitions = [
        ("qualified_start_rate", "Qualified starts divided by sessions", "Primary engagement", "Daily feature device mart", "product analytics"),
        ("day7_retention_rate", "Accounts active seven days after feature exposure divided by exposed accounts", "Retention", "Experiment cohort table", "lifecycle analytics"),
        ("conversion_rate", "Target action completions divided by eligible exposed accounts", "Primary conversion", "Experiment result table", "product analytics"),
        ("avg_watch_minutes", "Average watch minutes per active account", "Engagement depth", "Playback fact table", "analytics engineering"),
        ("playback_start_ms", "Median playback startup latency in milliseconds", "Guardrail", "Playback quality logs", "playback engineering"),
        ("rebuffer_rate", "Sessions with rebuffering divided by playback sessions", "Guardrail", "Playback quality logs", "playback engineering"),
        ("search_success_rate", "Search sessions with a title detail view or play within ten minutes", "Discovery quality", "Search event stream", "search product"),
        ("data_quality_score", "Weighted score from freshness, completeness, duplicate exposure, and join coverage checks", "Trust", "Analytics quality checks", "data platform"),
    ]
    metric_rows = [
        {
            "metric_name": name,
            "definition": definition,
            "metric_role": role,
            "source_table": source,
            "owner": owner,
        }
        for name, definition, role, source, owner in metric_definitions
    ]

    experiments = [
        ("EXP001", "F002", "A/B", "Ranking personalization increases qualified starts without rebuffer regression.", "qualified_start_rate", 0.024, 0.004),
        ("EXP002", "F003", "Multivariate", "Preview length and audio state increase title discovery while keeping exits stable.", "conversion_rate", 0.018, 0.002),
        ("EXP003", "F007", "A/B", "Ad pod spacing improves completion while protecting watch minutes.", "day7_retention_rate", 0.011, 0.009),
        ("EXP004", "F008", "Multivariate", "Intent rewrite improves successful search sessions for ambiguous queries.", "search_success_rate", 0.031, 0.003),
        ("EXP005", "F011", "A/B", "Reminder timing lifts day-seven retention for episodic viewers.", "day7_retention_rate", 0.019, 0.002),
    ]
    experiment_rows = []
    experiment_readouts = []
    for exp_id, feature_id, test_type, hypothesis, primary_metric, modeled_lift, guardrail_penalty in experiments:
        feature = next(item for item in features if item[0] == feature_id)
        variants = ["control", "treatment"] if test_type == "A/B" else ["control", "short_preview", "immersive_preview"]
        segment_results = []
        for segment, s_meta in segments.items():
            base_rate = s_meta["conversion"]
            if primary_metric == "day7_retention_rate":
                base_rate = s_meta["retention"]
            if primary_metric == "search_success_rate":
                base_rate = 0.72 if segment != "New trial households" else 0.61
            if primary_metric == "qualified_start_rate":
                base_rate = 0.47 if segment != "Ad-supported explorers" else 0.38
            control_users = random.randint(14500, 42000)
            treatment_users = random.randint(14500, 42000)
            control_rate = max(0.08, min(0.78, base_rate + random.uniform(-0.012, 0.012)))
            segment_lift = modeled_lift + random.uniform(-0.011, 0.016)
            if segment == "New trial households" and feature_id in ["F002", "F003", "F008"]:
                segment_lift += random.uniform(0.008, 0.018)
            if segment == "Ad-supported explorers" and feature_id == "F007":
                segment_lift -= random.uniform(0.004, 0.011)
            treatment_rate = max(0.08, min(0.82, control_rate + segment_lift))
            control_success = int(control_users * control_rate)
            treatment_success = int(treatment_users * treatment_rate)
            control_watch = 28 * s_meta["watch"] * random.uniform(0.94, 1.06)
            treatment_watch = control_watch * (1 + modeled_lift * 0.9 - guardrail_penalty + random.uniform(-0.015, 0.025))
            control_error = device_mod[feature[3]]["rebuffer"] + random.uniform(-0.002, 0.003)
            treatment_error = control_error + guardrail_penalty + random.uniform(-0.002, 0.003)
            p_value = two_prop_p_value(control_success, control_users, treatment_success, treatment_users)
            segment_results.append((segment, treatment_rate - control_rate, p_value, treatment_error - control_error))
            for variant in variants:
                if variant == "control":
                    users = control_users
                    success = control_success
                    rate = control_rate
                    watch = control_watch
                    error = control_error
                else:
                    variant_bonus = 1 if variant == "treatment" else 0.88 if variant == "short_preview" else 1.14
                    users = treatment_users
                    rate = max(0.08, min(0.82, control_rate + segment_lift * variant_bonus))
                    success = int(users * rate)
                    watch = treatment_watch * variant_bonus if variant != "short_preview" else treatment_watch * 0.96
                    error = treatment_error + (0.002 if variant == "immersive_preview" else 0)
                experiment_rows.append(
                    {
                        "experiment_id": exp_id,
                        "feature_id": feature_id,
                        "feature_name": feature[1],
                        "test_type": test_type,
                        "customer_segment": segment,
                        "variant": variant,
                        "users": users,
                        "primary_metric": primary_metric,
                        "metric_successes": success,
                        "metric_rate": pct(rate),
                        "avg_watch_minutes": rounded(watch, 2),
                        "playback_error_rate": pct(max(0.001, error)),
                        "startup_latency_ms": int(device_mod[feature[3]]["startup"] * random.uniform(0.92, 1.16)),
                    }
                )
        avg_lift = sum(item[1] for item in segment_results) / len(segment_results)
        min_p = min(item[2] for item in segment_results)
        guardrail_delta = max(item[3] for item in segment_results)
        winning_segment = max(segment_results, key=lambda item: item[1])[0]
        risk_segment = max(segment_results, key=lambda item: item[3])[0]
        quality = sum(row["score"] for row in quality_rows if row["feature_id"] == feature_id) / len(check_types)
        confidence = max(0.42, min(0.98, 1 - min_p * 2))
        business_impact = sum(int(row["active_accounts"]) for row in daily_rows if row["feature_id"] == feature_id) / 120
        decision = "launch" if min_p < 0.05 and guardrail_delta < 0.004 and quality >= 84 else "iterate" if min_p < 0.12 and quality >= 78 else "hold"
        if guardrail_delta >= 0.006 or quality < 78:
            decision = "hold"
        experiment_readouts.append(
            {
                "experiment_id": exp_id,
                "feature_id": feature_id,
                "feature_name": feature[1],
                "test_type": test_type,
                "hypothesis": hypothesis,
                "primary_metric": primary_metric,
                "avg_lift_pct": rounded(avg_lift * 100, 2),
                "best_segment": winning_segment,
                "risk_segment": risk_segment,
                "min_p_value": round(min_p, 4),
                "guardrail_delta_pct": rounded(guardrail_delta * 100, 2),
                "data_quality_score": rounded(quality, 1),
                "confidence_score": rounded(confidence * 100, 1),
                "estimated_accounts_reached": int(business_impact),
                "decision": decision,
            }
        )

    aggregates = defaultdict(lambda: defaultdict(float))
    for row in daily_rows:
        feature_id = row["feature_id"]
        aggregates[feature_id]["accounts"] += int(row["active_accounts"])
        aggregates[feature_id]["sessions"] += int(row["sessions"])
        aggregates[feature_id]["starts"] += int(row["qualified_starts"])
        aggregates[feature_id]["watch"] += float(row["avg_watch_minutes"]) * int(row["active_accounts"])
        aggregates[feature_id]["conversion"] += float(row["conversion_rate"]) * int(row["active_accounts"])
        aggregates[feature_id]["retention"] += float(row["day7_retention_rate"]) * int(row["active_accounts"])
        aggregates[feature_id]["startup"] += int(row["playback_start_ms"]) * int(row["sessions"])
        aggregates[feature_id]["rebuffer"] += float(row["rebuffer_rate"]) * int(row["sessions"])
        aggregates[feature_id]["quality"] += float(row["data_quality_score"])
        aggregates[feature_id]["rows"] += 1

    quality_by_feature = defaultdict(list)
    for row in quality_rows:
        quality_by_feature[row["feature_id"]].append(float(row["score"]))

    readout_by_feature = {row["feature_id"]: row for row in experiment_readouts}
    queue = []
    for feature in features:
        feature_id, name, area, device, tier, owner, stage, question = feature
        agg = aggregates[feature_id]
        accounts = agg["accounts"]
        sessions = agg["sessions"]
        start_rate = safe_div(agg["starts"], sessions)
        watch = safe_div(agg["watch"], accounts)
        conversion = safe_div(agg["conversion"], accounts)
        retention = safe_div(agg["retention"], accounts)
        startup = safe_div(agg["startup"], sessions)
        rebuffer = safe_div(agg["rebuffer"], sessions)
        data_quality = safe_div(sum(quality_by_feature[feature_id]), len(quality_by_feature[feature_id]))
        experiment = readout_by_feature.get(feature_id)
        lift = experiment["avg_lift_pct"] if experiment else random.uniform(0.4, 1.4)
        confidence = experiment["confidence_score"] if experiment else data_quality * 0.72
        guardrail_penalty = max(0, rebuffer - 0.012) * 420 + max(0, startup - 760) / 28
        opportunity = accounts / 100000 * (lift * 7.5 + (0.34 - retention) * 18 + (0.28 - conversion) * 12)
        priority = opportunity + confidence * 0.45 - guardrail_penalty + (100 - data_quality) * -0.32
        next_move = "ship with monitoring" if experiment and experiment["decision"] == "launch" else "iterate experiment" if experiment and experiment["decision"] == "iterate" else "fix measurement before decision" if data_quality < 82 else "add to roadmap review"
        queue.append(
            {
                "feature_id": feature_id,
                "feature_name": name,
                "product_area": area,
                "primary_device": device,
                "service_tier": tier,
                "business_owner": owner,
                "launch_stage": stage,
                "active_accounts": int(accounts / days),
                "qualified_start_rate": pct(start_rate),
                "avg_watch_minutes": rounded(watch, 1),
                "conversion_rate": pct(conversion),
                "day7_retention_rate": pct(retention),
                "playback_start_ms": int(startup),
                "rebuffer_rate": pct(rebuffer),
                "data_quality_score": rounded(data_quality, 1),
                "experiment_lift_pct": rounded(lift, 2),
                "confidence_score": rounded(confidence, 1),
                "priority_score": rounded(priority, 1),
                "next_move": next_move,
            }
        )
    queue.sort(key=lambda row: row["priority_score"], reverse=True)

    segment_summary = []
    for segment in segments:
        rows = [row for row in daily_rows if row["customer_segment"] == segment]
        accounts = sum(int(row["active_accounts"]) for row in rows)
        segment_summary.append(
            {
                "customer_segment": segment,
                "active_accounts": int(accounts / days),
                "avg_watch_minutes": rounded(sum(float(row["avg_watch_minutes"]) * int(row["active_accounts"]) for row in rows) / accounts, 1),
                "conversion_rate": pct(sum(float(row["conversion_rate"]) * int(row["active_accounts"]) for row in rows) / accounts),
                "day7_retention_rate": pct(sum(float(row["day7_retention_rate"]) * int(row["active_accounts"]) for row in rows) / accounts),
                "highest_response_feature": max(queue, key=lambda item: item["priority_score"] if item["product_area"] in ["Home", "Discovery", "Live", "Search", "Notifications"] else -999)["feature_name"],
            }
        )

    trust_queue = sorted(
        [
            {
                "feature_id": row["feature_id"],
                "feature_name": row["feature_name"],
                "check_type": row["check_type"],
                "score": row["score"],
                "status": row["status"],
                "owner": row["owner"],
                "recommended_fix": row["recommended_fix"],
            }
            for row in quality_rows
        ],
        key=lambda row: row["score"],
    )

    summary = {
        "modeled_rows": len(daily_rows) + len(experiment_rows) + len(quality_rows) + len(request_rows),
        "daily_metric_rows": len(daily_rows),
        "experiment_rows": len(experiment_rows),
        "features": len(features),
        "tests": len(experiments),
        "avg_data_quality": rounded(sum(row["data_quality_score"] for row in queue) / len(queue), 1),
        "top_priority": queue[0],
        "top_experiment": max(experiment_readouts, key=lambda row: row["confidence_score"]),
        "trust_risk": trust_queue[0],
        "launch_recommendations": sum(1 for row in experiment_readouts if row["decision"] == "launch"),
        "hold_recommendations": sum(1 for row in experiment_readouts if row["decision"] == "hold"),
    }

    write_csv(DATA / "product_features.csv", feature_rows, list(feature_rows[0]))
    write_csv(DATA / "daily_feature_metrics.csv", daily_rows, list(daily_rows[0]))
    write_csv(DATA / "experiment_results.csv", experiment_rows, list(experiment_rows[0]))
    write_csv(DATA / "metric_definitions.csv", metric_rows, list(metric_rows[0]))
    write_csv(DATA / "data_quality_checks.csv", quality_rows, list(quality_rows[0]))
    write_csv(DATA / "stakeholder_requests.csv", request_rows, list(request_rows[0]))
    write_csv(OUTPUTS / "product_priority_queue.csv", queue, list(queue[0]))
    write_csv(OUTPUTS / "experiment_readouts.csv", experiment_readouts, list(experiment_readouts[0]))
    write_csv(OUTPUTS / "segment_summary.csv", segment_summary, list(segment_summary[0]))
    write_csv(OUTPUTS / "metric_trust_queue.csv", trust_queue, list(trust_queue[0]))
    (OUTPUTS / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    data_payload = {
        "summary": summary,
        "priorityQueue": queue[:8],
        "experimentReadouts": experiment_readouts,
        "segmentSummary": segment_summary,
        "trustQueue": trust_queue[:10],
        "metricDefinitions": metric_rows,
        "stakeholderRequests": request_rows[:8],
    }
    (SRC / "data.js").write_text(
        "window.STREAMING_PRODUCT_DATA = " + json.dumps(data_payload, indent=2) + ";\n",
        encoding="utf-8",
    )

    (ANALYSIS / "executive_findings.md").write_text(
        "\n".join(
            [
                "# Executive Findings",
                "",
                "## What I analyzed",
                "",
                f"I generated {len(daily_rows):,} daily feature, device, and customer-segment rows, {len(experiment_rows):,} experiment result rows, {len(quality_rows):,} metric quality checks, and {len(request_rows):,} stakeholder requests for a digital entertainment product analytics workflow.",
                "",
                "## Findings",
                "",
                f"- The top product decision is {queue[0]['feature_name']} on {queue[0]['primary_device']}, with a priority score of {queue[0]['priority_score']}.",
                f"- The strongest experiment readout is {summary['top_experiment']['experiment_id']} on {summary['top_experiment']['feature_name']}, with {summary['top_experiment']['avg_lift_pct']} percent average lift and {summary['top_experiment']['confidence_score']} confidence score.",
                f"- The weakest data trust signal is {trust_queue[0]['check_type']} for {trust_queue[0]['feature_name']}, owned by {trust_queue[0]['owner']}.",
                "",
                "## Recommendation",
                "",
                "Use the workbench as a weekly product analytics review: start with the product priority queue, validate experiment decisions against guardrails, then clear the lowest-trust metric checks before scaling recommendations into recurring reporting.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (ANALYSIS / "analysis_plan.md").write_text(
        "\n".join(
            [
                "# Analysis Plan",
                "",
                "1. Translate stakeholder questions into feature, device, service tier, and customer-segment cuts.",
                "2. Build a daily metric mart with engagement, conversion, retention, playback quality, and data quality signals.",
                "3. Read experiment outcomes with a primary metric, guardrails, segment heterogeneity, and data quality checks.",
                "4. Rank product decisions by opportunity size, statistical confidence, user impact, and metric trust.",
                "5. Convert findings into launch, iterate, hold, or data-fix recommendations for product and business stakeholders.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (ANALYSIS / "methodology.md").write_text(
        "\n".join(
            [
                "# Methodology",
                "",
                "The generator uses a fixed random seed and synthetic data shaped like a streaming product analytics warehouse. It creates feature metadata, daily feature-device-segment metrics, experiment result rows, metric definitions, data quality checks, stakeholder requests, and analysis outputs.",
                "",
                "Experiment readouts use two-proportion z-tests for primary metric movement, guardrail deltas for playback quality, and a decision rule that combines statistical confidence, guardrail safety, and metric trust.",
                "",
                "The product priority score combines estimated opportunity, experiment lift, confidence, playback guardrail risk, retention gap, conversion gap, and data quality score. The score is directional and meant to support prioritization, not to automate launch decisions.",
                "",
            ]
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    build()
