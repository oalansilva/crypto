
trades = [
    -0.0614, 6.2005, 1.3625, -0.0614, -0.0614, 3.1879, -0.0614, 0.3041, -0.0614, 0.0605,
    -0.0614, -0.0614, -0.0614, -0.0614, -0.0115, -0.0614, -0.0614, 0.4944, -0.0614, -0.0614,
    -0.0614, -0.0453, 0.0224, -0.0283, -0.0614, 0.2094, -0.0015, 3.6454, -0.0614, 0.7771,
    0.0212, -0.0614, -0.0614, 0.4864, -0.0614, -0.0614, 0.2071, 0.0433, 0.0973, -0.0614, -0.0614
]

capital = 100.0
print(f"Starting Capital: {capital}")

for i, t in enumerate(trades):
    prev = capital
    capital = capital * (1 + t)
    print(f"Trade {i+1}: {t*100:+.2f}% -> {capital:.2f}")

total_return_compound = (capital - 100.0) / 100.0 * 100.0
print(f"\nFinal Capital (Compounded): {capital:.2f}")
print(f"Calculated Total Return (Compounded): {total_return_compound:.2f}%")

simple_sum = sum(t * 100 for t in trades)
print(f"Calculated Total Return (Simple Sum): {simple_sum:.2f}%")
