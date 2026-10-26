/**
 * Blocos visuais da Descoberta multiclasse (card #1121), conforme o protótipo aprovado
 * (`frontend/public/prototypes/card-1121-descoberta-acoes-etfs/`): bloco compacto do candidato, linha de
 * amostra insuficiente, identidade da execução no modal e o quadro "Por ativo".
 */

import { forwardRef } from 'react'
import { CircleCheck, CircleX, Clock, Info, Loader, TriangleAlert } from 'lucide-react'
import { CLASS_LABEL, type AssetClass } from '../lib/assetSelection'
import {
  ASSET_PAGE,
  assetStateView,
  countText,
  modalSampleText,
  rowBlock,
  type MulticlassRow,
  type StateIcon,
  type SweepAsset,
  type SweepStateName,
  type Tone,
} from '../lib/discoveryMulticlass'

function ToneIcon({ tone }: { tone: Tone }) {
  return tone === 'warn' ? <TriangleAlert aria-hidden="true" /> : <Info aria-hidden="true" />
}

export function ClassChip({ cls, currency, joiner = ' ' }: { cls: AssetClass; currency: string; joiner?: string }) {
  return (
    <>
      <span className="mc-cls" data-class={cls}>
        {CLASS_LABEL[cls]}
      </span>
      {joiner}
      <span className="mc-cur">{currency}</span>
    </>
  )
}

/**
 * Bloco do candidato em duas linhas lógicas (decisão 11): identidade + precisão; convenções + período efetivo.
 * `withLead` (Decidir) mostra "NVDA · 1d · Long"; as Parciais já trazem o mercado na linha de cima.
 */
export function CandidateBlock({ row, withLead }: { row: MulticlassRow; withLead: boolean }) {
  const block = rowBlock(row)
  const { precision } = block
  const split = precision.short !== precision.full
  return (
    <span
      className="mc-rowdata"
      data-asset={row.symbol}
      data-asset-class={block.cls}
      data-tf={row.timeframe}
      data-testid="candidate-class-block"
    >
      <span className="mc-l1">
        {withLead ? (
          <>
            <span className="mc-g">
              <b>{row.symbol}</b> · {row.timeframe} · {row.direction === 'short' ? 'Short' : 'Long'}
            </span>{' '}
          </>
        ) : null}
        <span className="mc-g">
          <ClassChip cls={block.cls} currency={block.currency} />
        </span>{' '}
        <span className="mc-g mc-prec" data-tone={precision.tone} data-testid="mc-precision" title={precision.full}>
          <ToneIcon tone={precision.tone} />
          {split ? (
            <>
              <span aria-hidden="true">{precision.short}</span>
              <span className="sr-only">{precision.full}</span>
            </>
          ) : (
            <span>{precision.short}</span>
          )}
        </span>
      </span>
      <span className="mc-l2">
        <span className="mc-conv">{block.conventions.replace(/ · /g, ' · ')}</span>{' '}
        {block.period ? (
          <span className="mc-g">
            <span className="sr-only">Período efetivo </span>
            <span title="Período efetivo">{block.period}</span>
          </span>
        ) : null}
      </span>
    </span>
  )
}

/** Linha de amostra insuficiente no Decidir: motivo no lugar da precisão e "Período efetivo: nenhum candle". */
export function InsufficientBlock({ row, reason }: { row: MulticlassRow; reason: string | null }) {
  const block = rowBlock(row)
  const text = reason ? reason.charAt(0).toUpperCase() + reason.slice(1) : 'Amostra insuficiente'
  return (
    <span
      className="mc-rowdata"
      data-asset={row.symbol}
      data-asset-class={block.cls}
      data-tf={row.timeframe}
      data-insufficient=""
      data-testid="candidate-class-block"
    >
      <span className="mc-l1">
        <span className="mc-g">
          <b>{row.symbol}</b> · {row.timeframe} · {row.direction === 'short' ? 'Short' : 'Long'}
        </span>{' '}
        <span className="mc-g">
          <ClassChip cls={block.cls} currency={block.currency} />
        </span>{' '}
        <span className="mc-prec" data-tone="warn">
          <TriangleAlert aria-hidden="true" />
          <span>{text}</span>
        </span>
      </span>
      <span className="mc-l2">
        <span className="mc-conv">{block.conventions.replace(/ · /g, ' · ')}</span>{' '}
        <span className="mc-g">Período efetivo: nenhum candle</span>
      </span>
    </span>
  )
}

/** Identidade da execução no modal de promoção (decisão 10): o trecho de precisão vem por extenso. */
export function ModalIdentity({ row }: { row: MulticlassRow }) {
  const block = rowBlock(row)
  return (
    <span className="mc-rowdata mc-modal-id" data-testid="modal-execution-identity">
      <span className="mc-symline">
        <ClassChip cls={block.cls} currency={block.currency} joiner=" · " />
      </span>
      <span className="mc-prec" data-tone={block.precision.tone}>
        <ToneIcon tone={block.precision.tone} />
        <span>{block.precision.full}</span>
      </span>
      <span className="mc-conv">{block.conventions}</span>
      {block.period ? <span className="mc-conv">Período efetivo {block.period}</span> : null}
      <span className="mc-conv" data-testid="modal-sample">
        {modalSampleText(row)}
      </span>
    </span>
  )
}

function StateIconView({ icon }: { icon: StateIcon }) {
  switch (icon) {
    case 'ok':
      return <CircleCheck aria-hidden="true" />
    case 'warn':
      return <TriangleAlert aria-hidden="true" />
    case 'fail':
      return <CircleX aria-hidden="true" />
    case 'load':
      return <Loader aria-hidden="true" />
    case 'info':
      return <Info aria-hidden="true" />
    default:
      return <Clock aria-hidden="true" />
  }
}

interface AssetsBoardProps {
  assets: SweepAsset[]
  sweepState: SweepStateName
  limit: number
  onMore: () => void
  live: string
}

/** Quadro "Por ativo" (decisão 7): lista ordenada, 50 por vez, cabeçalhos acima de 620 px e cartão abaixo. */
export const AssetsBoard = forwardRef<HTMLHeadingElement, AssetsBoardProps>(function AssetsBoard(
  { assets, sweepState, limit, onMore, live },
  titleRef,
) {
  const shown = assets.slice(0, limit)
  const rest = assets.length - shown.length
  return (
    <section className="mc-assets mb-4" aria-labelledby="mc-assets-title" data-testid="sweep-assets">
      <div className="mc-assets-head">
        <h2 id="mc-assets-title" ref={titleRef} tabIndex={-1}>
          Por ativo
        </h2>
        <p>
          Classe, moeda e estado de cada ativo da varredura. Amostra insuficiente e falha ficam aqui com o motivo e nunca
          viram candidato. O ativo em curso, as falhas e as amostras insuficientes ficam no topo; a lista mostra 50 ativos
          por vez.
        </p>
      </div>
      <p className="sr-only" role="status" aria-live="polite" data-testid="assets-live">
        {live}
      </p>
      <div className="mc-asset-cols" aria-hidden="true">
        <span>Ativo</span>
        <span>Combinações</span>
        <span>Estado</span>
        <span>Detalhe</span>
      </div>
      <ol className="mc-asset-list" data-testid="asset-list">
        {shown.map((asset) => {
          const cls: AssetClass = asset.asset_class ?? (asset.symbol.includes('/') ? 'crypto' : 'stock')
          const view = assetStateView(asset, sweepState)
          return (
            <li key={asset.symbol} data-asset={asset.symbol} data-state={view.key}>
              <span className="mc-asset">
                <b>{asset.symbol}</b>
                <span className="mc-g">
                  <ClassChip cls={cls} currency={asset.currency || (cls === 'crypto' ? 'USDT' : 'USD')} />
                </span>
              </span>
              <span className="mc-count">
                <span className="sr-only">Combinações: </span>
                {countText(asset)}
              </span>
              <span className="mc-state" data-state={view.key}>
                <StateIconView icon={view.icon} />
                <span>
                  <span className="sr-only">Estado: </span>
                  {view.label}
                </span>
              </span>
              <span className="mc-detail">
                {view.detail ? (
                  <>
                    <span className="sr-only">Detalhe: </span>
                    {view.detail}
                  </>
                ) : null}
              </span>
            </li>
          )
        })}
      </ol>
      {rest > 0 ? (
        <div className="mc-assets-more">
          <button type="button" className="mc-more-btn" onClick={onMore} data-testid="assets-more">
            Mostrar mais {Math.min(ASSET_PAGE, rest)}
          </button>{' '}
          <span data-testid="assets-more-count">
            Mostrando {shown.length} de {assets.length} ativos
          </span>
        </div>
      ) : null}
    </section>
  )
})
