## MODIFIED Requirements

### Requirement: Monitor chart modal keeps saved favorite parity
The Monitor chart modal SHALL treat the saved favorite id as the identity for chart parity with Favorites and SHALL not render a divergent marker source when favorite analysis data is available.

#### Scenario: Monitor card shows Venda and Favorite chart has sell marker
- **WHEN** a Monitor opportunity for a saved favorite is classified as `Venda`
- **AND** the Favorite analysis payload includes a sell trade for the same favorite
- **THEN** opening `Abrir Gráfico` from Monitor SHALL show the sell marker from the favorite analysis trade set
- **AND** the chart marker source SHALL not be limited to the opportunity `signal_history`.

#### Scenario: Monitor and Favorites use same favorite id
- **WHEN** Monitor and Favorites refer to the same `favorite_id`
- **THEN** both chart paths SHALL resolve trades and candles from the same favorite analysis payload where permitted.
