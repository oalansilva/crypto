## REMOVED Requirements

### Requirement: Favoritar ação ou ETF é recusado até o #1122
**Reason**: O #1122 traz a atualização diária, o Monitor e os alertas de ação e ETF, que eram o motivo da recusa (#1119, decisão 15).
**Migration**: `POST /api/favorites/` aceita ação e ETF e "Salvar nos Favoritos" do resultado abre o modal, conforme `favorite-configuration-identity` ("Ação e ETF são favoritáveis como a cripto"). O código `asset_class_not_favoritable` sai.
