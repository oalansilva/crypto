## ADDED Requirements

### Requirement: Overlays de média não avançam à frente da última vela carregada
Os gráficos partilhados da análise (`/combo/results`) e do Monitor SHALL clipar overlays de média (SMA/EMA ou equivalente) ao timestamp da última vela realmente carregada, inclusive quando pontos vivos do Monitor são misturados à série em cache.

#### Scenario: Mix de média viva com velas de snapshot
- **WHEN** a tela mistura pontos de média do Monitor até o presente com velas que pararam antes
- **THEN** o overlay MUST NOT pintar à frente da última vela carregada
- **AND** o gráfico MUST NOT mostrar buraco à direita com linha solta

#### Scenario: Análise e Monitor no mesmo recorte
- **WHEN** o operador compara o gráfico da análise e o gráfico do Monitor para o mesmo par/intervalo
- **THEN** em ambos a média termina na última vela carregada dessa tela
