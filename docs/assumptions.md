# Parameter and uncertainty provenance

## Supplied facts

See data/supplied_case.json and the official 2026 UPC Problem B. Positions refer to the ball center. The initial position and times are assumed exact, because their errors are not given.

## Geometry and material constants

- Mass 0.43 kg and radius 0.11 m: representative modeling choices, consistent with IFAB Law 2 (410--450 g, circumference 68--70 cm). Source: https://www.theifab.com/laws/latest/the-ball/. These are not measurements of this particular ball.
- Area pi*radius^2 m^2: derived geometry.
- g=9.81 m/s^2, density=1.225 kg/m^3: nominal environmental assumptions, also used in Linthorne and Patel (2011). They do not identify venue conditions.

## Aerodynamics

Asai and Seo, Aerodynamic drag of modern soccer balls, SpringerPlus 2:171 (2013), DOI 10.1186/2193-1801-2-171, verified at https://tsukuba.repo.nii.ac.jp/records/29043. Different ball constructions produce different drag behavior. This supports varying drag, not a measured prior for the unknown supplied ball.

Linthorne and Patel, Optimum Projection Angle for Attaining Maximum Distance in a Soccer Punt Kick, Journal of Sports Science and Medicine 10(1):203--214 (2011), verified full text https://pmc.ncbi.nlm.nih.gov/articles/PMC3737918/. The study uses 0.43 kg, area 0.038 m^2, density 1.225 kg/m^3 and distinguishes spin-dependent lift and drag. Its punt-kick population is not a penalty-kick calibration dataset. No DOI is asserted for this article.

Myers and Mitchell, A mathematical analysis of the motion of an in-flight soccer ball, Sports Engineering 16(1):29--41 (2013), DOI 10.1007/s12283-012-0105-8, verified author-university metadata: https://pure.ul.ie/en/publications/a-mathematical-analysis-of-the-motion-of-an-in-flight-soccer-ball/. It motivates three-dimensional coupled aerodynamics; it does not establish our numerical prior.

All distributions below are ASSUMED RANGES FOR SENSITIVITY ANALYSIS, not empirical frequency distributions: Cd uniform [0.12,0.40], spin magnitude uniform [0,80] rad/s (0--12.7 revolutions/s), isotropic spin axis, density uniform [1.15,1.30] kg/m^3. Nominal Model 1 uses Cd=0.25 and zero spin. Model 2 uses the reduced linear lift law Cl=alpha*R*|omega|/|v|, alpha=1, with force direction weighted by sin(angle(omega,v)). Thus a_M=(rho*A/(2m))*alpha*R*(omega cross v). Alpha and spin cannot be identified separately; alpha is fixed. This simplified law is an assumption, not a fit quoted from a paper. Lift saturation and speed-dependent drag are tested only in the declared mismatch experiment.

## Measurement and population

Independent zero-mean isotropic Gaussian error on each later coordinate; sigma=0.005,0.01,0.02,0.05 m are scenarios. No camera specification was supplied. No timing error, calibration bias, wind, ball deformation or spin decay in the main model.

Synthetic velocities: speed uniform [22,35] m/s; azimuth uniform [-22,22] degrees; elevation uniform [5,18] degrees. These define a synthetic test population, not measured FIFA statistics. No selection by goal/miss outcome. Matched physics is an internal consistency test. A separate nonlinear-lift/speed-dependent-drag population tests limited mismatch; neither establishes real-world accuracy.

Goal probability means center inside the stated rectangle at the first plane crossing while airborne. A separate radius-clearance probability uses |y|<3.55 m and 0.11<z<2.33 m. Neither includes goalkeeper action or constitutes a rule-complete probability of a goal. Ground contact occurs at z=0.11 m on downward motion. No bounce model is extrapolated.
