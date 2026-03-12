oBeVisible[2m([22m[2m)[22m failed

    Locator: getByText('HBAR', { exact: true })
    Expected: visible
    Error: strict mode violation: getByText('HBAR', { exact: true }) resolved to 2 elements:
        1) <div class="truncate font-extrabold tracking-[0.2px] text-white">HBAR</div> aka getByText('HBAR').first()
        2) <div class="font-extrabold tracking-[0.2px] text-white">HBAR</div> aka getByText('HBAR').nth(1)

    Call log:
    [2m  - Expect "toBeVisible" with timeout 5000ms[22m
    [2m  - waiting for getByText('HBAR', 