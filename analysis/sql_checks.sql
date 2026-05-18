-- Feature health mart for weekly product review.
select
  feature_id,
  feature_name,
  product_area,
  device_family,
  service_tier,
  sum(active_accounts) as active_accounts,
  sum(qualified_starts) / nullif(sum(sessions), 0) as qualified_start_rate,
  sum(avg_watch_minutes * active_accounts) / nullif(sum(active_accounts), 0) as avg_watch_minutes,
  sum(conversion_rate * active_accounts) / nullif(sum(active_accounts), 0) as conversion_rate,
  sum(day7_retention_rate * active_accounts) / nullif(sum(active_accounts), 0) as day7_retention_rate,
  sum(playback_start_ms * sessions) / nullif(sum(sessions), 0) as playback_start_ms,
  sum(rebuffer_rate * sessions) / nullif(sum(sessions), 0) as rebuffer_rate,
  avg(data_quality_score) as data_quality_score
from daily_feature_metrics
group by 1, 2, 3, 4, 5
order by active_accounts desc;

-- Experiment readout with primary metric movement by segment.
with arms as (
  select
    experiment_id,
    feature_id,
    customer_segment,
    variant,
    sum(users) as users,
    sum(metric_successes) as metric_successes,
    sum(metric_successes) / nullif(sum(users), 0) as metric_rate,
    avg(playback_error_rate) as playback_error_rate,
    avg(startup_latency_ms) as startup_latency_ms
  from experiment_results
  group by 1, 2, 3, 4
),
control as (
  select * from arms where variant = 'control'
),
treatment as (
  select * from arms where variant <> 'control'
)
select
  treatment.experiment_id,
  treatment.feature_id,
  treatment.customer_segment,
  treatment.variant,
  treatment.metric_rate - control.metric_rate as metric_lift,
  treatment.playback_error_rate - control.playback_error_rate as playback_error_delta,
  treatment.startup_latency_ms - control.startup_latency_ms as startup_latency_delta
from treatment
join control
  on treatment.experiment_id = control.experiment_id
 and treatment.feature_id = control.feature_id
 and treatment.customer_segment = control.customer_segment
order by metric_lift desc;

-- Metric trust checks before insight is scaled into recurring reporting.
select
  feature_id,
  feature_name,
  check_type,
  min(score) as weakest_score,
  count_if(status = 'fail') as failed_checks,
  count_if(status = 'watch') as watched_checks
from data_quality_checks
group by 1, 2, 3
having min(score) < 90
order by weakest_score asc;

-- Ad hoc product questions grouped by decision type.
select
  decision_needed,
  urgency,
  status,
  count(*) as request_count
from stakeholder_requests
group by 1, 2, 3
order by request_count desc;
