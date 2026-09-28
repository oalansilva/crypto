## MODIFIED Requirements

### Requirement: The ruler declares the homogeneity of the sample

The ruler SHALL declare the **model version** and the **confidence origin** of the eligible sample (from the per-cycle record) and the number of affected windows. An eligible sample that is **empty** SHALL NOT be homogeneous. A missing value or `unknown` on model version or on confidence origin SHALL NOT count as a declared value. The report SHALL call the sample **homogénea** only when every eligible window shares one declared model version and one declared origin. Otherwise the report SHALL call it **não verificada** when no declared pair exists (empty sample, or only missing/`unknown` values) and **não homogénea** when declared values are mixed. The affected-window count SHALL be the eligible windows that are not in that single declared pair, or all eligible windows when the sample is não verificada. Without a verified homogeneous sample the ruler SHALL NOT propose a threshold.

#### Scenario: Unknown or empty is not homogeneous

- **WHEN** the eligible sample is empty, or its model version or confidence origin is missing or `unknown`
- **THEN** the report SHALL label the sample não verificada (or não homogénea when declared values are mixed)
- **AND** SHALL show the number of affected windows
- **AND** SHALL NOT propose a threshold

#### Scenario: A mixed sample blocks the threshold

- **WHEN** the sample mixes declared confidence origins or declared model versions
- **THEN** the report SHALL declare the mixture and the affected windows
- **AND** no threshold SHALL be proposed for that regime

#### Scenario: A homogeneous sample is declared

- **WHEN** the sample has a single declared model version and a single declared confidence origin, with no missing or `unknown` value
- **THEN** the report SHALL declare that version and origin as homogénea
- **AND** a threshold may be proposed from it when the other ruler gates pass
