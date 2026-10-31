# landing-legal-pages Specification

## Purpose
TBD - created by archiving change card-1160-landing-auditoria. Update Purpose after archive.
## Requirements
### Requirement: Landing footer with trust links and risk notice
The landing SHALL end with a footer that links to the Privacy Policy (`/privacidade`) and the Terms of Use (`/termos`), carries a short risk notice, a signup CTA and the "Já tenho acesso" link. The footer SHALL NOT show a responsible person's name, CNPJ, contact or social networks.

#### Scenario: Visitor reaches the end of the landing
- **WHEN** a visitor scrolls to the bottom of `https://criptofarol.com.br/`
- **THEN** the footer SHALL show links "Política de Privacidade" and "Termos de Uso"
- **AND** it SHALL show the risk notice saying the product does not make investment recommendations, that investing in crypto, stocks and ETFs carries risk of loss, and that past results, including backtests, do not guarantee future results
- **AND** it SHALL NOT show a person's name, CNPJ, e-mail, phone or social network link

### Requirement: Real Privacy Policy and Terms pages
`/privacidade` and `/termos` SHALL be static pages served by the landing (not the SPA), with the landing header and footer. The Privacy Policy SHALL describe only what the form and PostHog actually collect: name and e-mail (step 1), optional WhatsApp, crypto level and difficulty (step 2), attribution stored in the browser (`criptofarol_attribution`), the PostHog events and the random identifier it stores in the browser, the Telegram notice to the team, which third parties receive data and which of them are outside Brazil (PostHog and Telegram), that the landing's PostHog runs without session recording or surveys, purposes, legal basis, retention, the channel for data-subject requests, `contato@criptofarol.com.br` (inside the policy, never in the footer), and the data-subject rights. Per Alan's answer at Design approval (T7), the policy SHALL NOT identify the data controller. It SHALL cover only the public page and the beta form, and SHALL NOT make claims about the logged-in app. The Terms SHALL apply to whoever uses the page (and, once invited, the product), without requiring acceptance in the signup form, and SHALL state that the product is decision support and not an investment recommendation, the risk, the closed-beta rules (waves, no guaranteed seat, 6 free months, no automatic charge), the Binance account rules (never asks for the password, never withdraws, each order needs confirmation), that stocks and ETFs are only followed and alerted (buying and selling through the Farol is crypto only), and the applicable law. The texts SHALL be the ones Alan approves at Design approval.

#### Scenario: Visitor opens the Privacy Policy
- **WHEN** a visitor opens `https://criptofarol.com.br/privacidade`
- **THEN** the response SHALL be the Privacy Policy page with status 200 and `text/html`
- **AND** it SHALL NOT be the SPA shell

#### Scenario: Policy matches what is collected
- **WHEN** the form or the analytics events change what they collect
- **THEN** the Privacy Policy SHALL be updated in the same change
- **AND** the policy SHALL NOT list data the landing does not collect

#### Scenario: Policy gives the request channel and does not identify the controller
- **WHEN** a visitor reads the data-subject rights section of the Privacy Policy
- **THEN** it SHALL give `contato@criptofarol.com.br` as the channel for access, correction and deletion requests
- **AND** it SHALL NOT identify the data controller
- **AND** the channel SHALL NOT appear in the footer

#### Scenario: Third parties and international transfer
- **WHEN** a visitor reads who receives data
- **THEN** the policy SHALL list PostHog and Telegram as services outside Brazil
- **AND** it SHALL NOT list a font or image provider, because the landing serves its own fonts and images

#### Scenario: Visitor opens the Terms
- **WHEN** a visitor opens `https://criptofarol.com.br/termos`
- **THEN** the response SHALL be the Terms of Use page with status 200 and `text/html`

### Requirement: Risk notice visible from the hero
The hero SHALL show a short risk sentence below the CTAs, visible without scrolling at 1440px and at 390px after the CTAs: "Apoio à decisão, não recomendação de investimento. Cripto, ações e ETFs têm risco, e nenhuma análise garante resultado." (wording widened to stocks and ETFs at Alan's T6, 29/10/2026).

#### Scenario: Visitor sees the first screen
- **WHEN** a visitor opens the landing at 1440px or 390px
- **THEN** the hero SHALL show the risk sentence right after the CTAs and the trust row

### Requirement: Consent line in the signup form
Step 1 of the signup form SHALL show "Ao enviar, você concorda com a Política de Privacidade." next to the submit button, with a link to `/privacidade` that opens in a new tab (`target="_blank"` with `rel="noopener"`), so the visitor does not lose what was typed.

#### Scenario: Visitor about to submit step 1
- **WHEN** a visitor views step 1 of the form
- **THEN** the consent line with the Privacy Policy link SHALL be visible next to the button
- **AND** opening the link SHALL keep the form, with the typed name and e-mail, in the original tab

