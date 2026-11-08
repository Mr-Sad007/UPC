# Independent review and resolutions

An independent OpenAI Codex reviewer inspected the core source, tests, frozen experiment plan, raw validation artifacts, article source and claim trace. No model identifier is asserted and no checksums were computed.

1. Missing M2 prediction regions could inflate coverage by dropping airborne truths. Fixed: all airborne M2 truths enter the denominator, with missing regions uncovered. Regression test added. No completed main cases lacked a region.
2. Representative M2 status could hide numerical particle failure mass. Fixed: the aggregate explicitly reports particle failure probability as well as case-level failure. All completed main particle failure probabilities were zero.
3. A tangent launch with upward acceleration was prematurely assigned ground contact. Fixed in both analytical and physical models, with a regression test. All generated truth launches have positive elevation, so completed experiments were unaffected.
4. Abstract causal wording linked finite particles directly to undercoverage without an extended-window refinement control. Replaced with an association between low effective sample sizes and undercoverage.
5. An RMSE comparison was called an increase in statistical bias. Replaced with increase in prediction error, explicitly stating that RMSE does not separate bias and variance.

The reviewer verified that central uncertainty, spatial mode, common-case metrics, coverage, supplied posterior, prior sensitivity, duration results and maximum refinement displacement matched saved artifacts. The final test run by the reviewer passed 13 tests; a later PDF-boundary regression brought the main suite to 14.

The review did not independently reverify literature or rerun the full numerical experiment. Those limits are retained rather than reported as independent external validation.
