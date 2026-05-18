const data = window.STREAMING_PRODUCT_DATA;

const formatNumber = (value) =>
  new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(value);

const percent = (value, digits = 1) => `${(Number(value) * 100).toFixed(digits)}%`;

const compact = (value) =>
  new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);

const label = (value) => String(value).replaceAll("_", " ");
const pValue = (value) => (Number(value) < 0.001 ? "<0.001" : value);

function renderRows(rows, columns) {
  return rows
    .map(
      (row) => `
        <tr>
          ${columns
            .map((column) => {
              const value = row[column.key];
              return `<td>${column.render ? column.render(value, row) : value}</td>`;
            })
            .join("")}
        </tr>
      `,
    )
    .join("");
}

function decisionClass(decision) {
  if (decision === "launch") return "positive";
  if (decision === "hold") return "risk";
  return "watch";
}

function renderExperimentCards(experiments) {
  return experiments
    .map(
      (experiment) => `
        <article class="experiment-card ${decisionClass(experiment.decision)}">
          <div class="card-topline">
            <span>${experiment.experiment_id} | ${experiment.test_type}</span>
            <b>${experiment.decision}</b>
          </div>
          <h3>${experiment.feature_name}</h3>
          <p>${experiment.hypothesis}</p>
          <dl>
            <div><dt>Lift</dt><dd>${experiment.avg_lift_pct}%</dd></div>
            <div><dt>P value</dt><dd>${pValue(experiment.min_p_value)}</dd></div>
            <div><dt>Guardrail</dt><dd>${experiment.guardrail_delta_pct}%</dd></div>
            <div><dt>Best segment</dt><dd>${experiment.best_segment}</dd></div>
          </dl>
        </article>
      `,
    )
    .join("");
}

function renderSegmentBars(rows) {
  const max = Math.max(...rows.map((row) => row.active_accounts));
  return rows
    .map(
      (row) => `
        <li>
          <div>
            <span>${row.customer_segment}</span>
            <strong>${compact(row.active_accounts)} accounts</strong>
          </div>
          <i style="width:${Math.max(8, (row.active_accounts / max) * 100)}%"></i>
          <em>${row.avg_watch_minutes} min | ${percent(row.day7_retention_rate)} retained</em>
        </li>
      `,
    )
    .join("");
}

function renderMetricDefinitions(rows) {
  return rows
    .map(
      (row) => `
        <article>
          <span>${row.metric_role}</span>
          <h3>${label(row.metric_name)}</h3>
          <p>${row.definition}</p>
          <b>${row.source_table}</b>
        </article>
      `,
    )
    .join("");
}

function renderApp() {
  const { summary } = data;
  document.querySelector("#app").innerHTML = `
    <header class="hero">
      <nav class="topbar" aria-label="Workbench sections">
        <a href="#product-health">Health</a>
        <a href="#experiments">Experiments</a>
        <a href="#metric-trust">Metric trust</a>
      </nav>
      <section class="hero-grid">
        <div>
          <p class="eyebrow">Digital entertainment product analytics</p>
          <h1>Streaming Product Analytics Workbench</h1>
          <p class="hero-copy">A decision artifact for evaluating feature performance, customer behavior, experiment impact, and metric trust across connected TV, mobile, web, tablet, subscription, and ad-supported experiences.</p>
        </div>
        <aside class="brief-card">
          <span>Operating question</span>
          <strong>Which product features should leaders ship, iterate, pause, or clean up based on user behavior, experiment evidence, and data reliability?</strong>
        </aside>
      </section>
    </header>

    <main>
      <section class="metric-strip" aria-label="Modeled workbench scale">
        <article><span>Modeled rows</span><strong>${formatNumber(summary.modeled_rows)}</strong><em>source and output rows</em></article>
        <article><span>Daily metric mart</span><strong>${formatNumber(summary.daily_metric_rows)}</strong><em>feature-device-segment days</em></article>
        <article><span>Experiment readouts</span><strong>${summary.tests}</strong><em>A/B and multivariate</em></article>
        <article><span>Average trust</span><strong>${summary.avg_data_quality}</strong><em>metric quality score</em></article>
      </section>

      <section class="surface product-health" id="product-health">
        <div class="section-heading">
          <p class="eyebrow">Surface 1</p>
          <h2>Executive Product Health</h2>
          <p>Ranks product-feature decisions by opportunity, customer response, retention, playback guardrails, experiment lift, confidence, and data quality.</p>
        </div>
        <div class="health-grid">
          <article class="panel large-panel">
            <div class="panel-title">
              <span>Priority queue</span>
              <strong>${summary.top_priority.feature_name}</strong>
            </div>
            <table>
              <thead>
                <tr><th>Feature</th><th>Device</th><th>Lift</th><th>Trust</th><th>Next move</th></tr>
              </thead>
              <tbody>
                ${renderRows(data.priorityQueue.slice(0, 6), [
                  { key: "feature_name" },
                  { key: "primary_device" },
                  { key: "experiment_lift_pct", render: (value) => `${value}%` },
                  { key: "data_quality_score" },
                  { key: "next_move" },
                ])}
              </tbody>
            </table>
          </article>
          <article class="panel insight-panel">
            <span>Best current decision</span>
            <strong>${summary.top_priority.next_move}</strong>
            <p>${summary.top_priority.feature_name} has ${percent(summary.top_priority.qualified_start_rate)} qualified starts, ${summary.top_priority.avg_watch_minutes} average watch minutes, and ${summary.top_priority.confidence_score} confidence score.</p>
          </article>
          <article class="panel segment-panel">
            <div class="panel-title">
              <span>Customer behavior cuts</span>
              <strong>Segment health</strong>
            </div>
            <ul class="segment-bars">${renderSegmentBars(data.segmentSummary)}</ul>
          </article>
        </div>
      </section>

      <section class="surface experiments" id="experiments">
        <div class="section-heading">
          <p class="eyebrow">Surface 2</p>
          <h2>Experiment Readout Lab</h2>
          <p>Connects business hypotheses to statistical readouts, guardrail movement, segment heterogeneity, and launch guidance.</p>
        </div>
        <div class="experiment-grid">
          <article class="panel experiment-lead">
            <span>Strongest readout</span>
            <h3>${summary.top_experiment.feature_name}</h3>
            <p>${summary.top_experiment.hypothesis}</p>
            <dl>
              <div><dt>Primary metric</dt><dd>${label(summary.top_experiment.primary_metric)}</dd></div>
              <div><dt>Average lift</dt><dd>${summary.top_experiment.avg_lift_pct}%</dd></div>
              <div><dt>Confidence</dt><dd>${summary.top_experiment.confidence_score}</dd></div>
              <div><dt>Decision</dt><dd>${summary.top_experiment.decision}</dd></div>
            </dl>
          </article>
          <div class="experiment-stack">${renderExperimentCards(data.experimentReadouts)}</div>
        </div>
      </section>

      <section class="surface metric-trust" id="metric-trust">
        <div class="section-heading">
          <p class="eyebrow">Surface 3</p>
          <h2>Metrics And Data Trust</h2>
          <p>Shows the metric framework, SQL-ready quality checks, and stakeholder requests that determine whether a product insight can be trusted.</p>
        </div>
        <div class="trust-grid">
          <article class="panel trust-alert">
            <span>Lowest trust signal</span>
            <strong>${summary.trust_risk.feature_name}</strong>
            <p>${label(summary.trust_risk.check_type)} scored ${summary.trust_risk.score}. Owner: ${summary.trust_risk.owner}. Fix: ${summary.trust_risk.recommended_fix}.</p>
          </article>
          <article class="panel wide-panel">
            <div class="panel-title">
              <span>Metric quality queue</span>
              <strong>Checks before scale</strong>
            </div>
            <table>
              <thead>
                <tr><th>Feature</th><th>Check</th><th>Score</th><th>Status</th><th>Fix</th></tr>
              </thead>
              <tbody>
                ${renderRows(data.trustQueue.slice(0, 7), [
                  { key: "feature_name" },
                  { key: "check_type", render: label },
                  { key: "score" },
                  { key: "status" },
                  { key: "recommended_fix" },
                ])}
              </tbody>
            </table>
          </article>
          <section class="metric-cards" aria-label="Metric definitions">
            ${renderMetricDefinitions(data.metricDefinitions)}
          </section>
        </div>
      </section>
    </main>
  `;
}

renderApp();
