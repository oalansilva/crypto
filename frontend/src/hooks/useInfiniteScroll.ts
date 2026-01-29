import { useState, useEffect, useRef, useCallback } from 'react';

const DEFAULT_PAGE_SIZE = 24;
const SENTINEL_ROOT_MARGIN = '200px';

/**
 * Hook de paginação infinita: carrega mais itens ao rolar até perto do fim.
 * Usa IntersectionObserver no "sentinel" (ref) para disparar o load.
 *
 * @param items - Lista completa (já filtrada/ordenada)
 * @param pageSize - Quantos itens adicionar por "load more"
 * @param initialSize - Quantos itens exibir no primeiro render (default: pageSize)
 * @returns visibleItems, hasMore, sentinelRef, loadMore
 */
export function useInfiniteScroll<T>(
    items: T[],
    pageSize: number = DEFAULT_PAGE_SIZE,
    initialSize?: number
) {
    const init = initialSize ?? pageSize;
    const [visibleCount, setVisibleCount] = useState(() =>
        Math.min(init, items.length)
    );
    const sentinelRef = useRef<HTMLDivElement>(null);

    const loadMore = useCallback(() => {
        setVisibleCount((c) => Math.min(c + pageSize, items.length));
    }, [pageSize, items.length]);

    // Reset when source list changes (filtros, ordenação, etc.)
    useEffect(() => {
        setVisibleCount(Math.min(init, items.length));
    }, [items.length, init]);

    useEffect(() => {
        const el = sentinelRef.current;
        if (!el) return;

        const observer = new IntersectionObserver(
            (entries) => {
                if (!entries[0]?.isIntersecting) return;
                setVisibleCount((c) => Math.min(c + pageSize, items.length));
            },
            { root: null, rootMargin: SENTINEL_ROOT_MARGIN, threshold: 0 }
        );
        observer.observe(el);
        return () => observer.disconnect();
    }, [items.length, pageSize]);

    const visibleItems = items.slice(0, visibleCount);
    const hasMore = visibleCount < items.length;

    return { visibleItems, hasMore, sentinelRef, loadMore };
}
