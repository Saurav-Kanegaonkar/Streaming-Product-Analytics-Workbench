# Methodology

The generator uses a fixed random seed and synthetic data shaped like a streaming product analytics warehouse. It creates feature metadata, daily feature-device-segment metrics, experiment result rows, metric definitions, data quality checks, stakeholder requests, and analysis outputs.

Experiment readouts use two-proportion z-tests for primary metric movement, guardrail deltas for playback quality, and a decision rule that combines statistical confidence, guardrail safety, and metric trust.

The product priority score combines estimated opportunity, experiment lift, confidence, playback guardrail risk, retention gap, conversion gap, and data quality score. The score is directional and meant to support prioritization, not to automate launch decisions.
