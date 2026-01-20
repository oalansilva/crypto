
def simulate_search():
    # Target: Antiga
    TARGET = {'short': 3, 'med': 32, 'long': 37, 'stop': 2.7}
    
    print(f"🎯 ALVO: {TARGET}\n")

    # --- ROUND 1: EXPLORATION ---
    # Range: Full | Step: Indicators=5, Stop=0.5
    r1_short = list(range(3, 20 + 1, 5))  # 3, 8, 13, 18
    r1_med = list(range(10, 50 + 1, 5))   # 10, 15, ... 30, 35 ...
    r1_long = list(range(20, 100 + 1, 10)) # 20, 30, 40 ...
    r1_stop = [round(x * 0.1, 1) for x in range(10, 80, 5)] # 1.0, 1.5, 2.0, 2.5, 3.0...

    print(f"--- RODADA 1 (Passo 5 / 0.5%) ---")
    # Simulate finding the closest neighbor
    best_short = min(r1_short, key=lambda x: abs(x - TARGET['short'])) # Finds 3
    best_med = min(r1_med, key=lambda x: abs(x - TARGET['med']))     # Finds 30 or 35 (Let's say 30)
    best_long = min(r1_long, key=lambda x: abs(x - TARGET['long']))   # Finds 40 (closer to 37 than 30? 37-30=7, 40-37=3. Yes 40)
    best_stop = min(r1_stop, key=lambda x: abs(x - TARGET['stop']))   # Finds 2.5 or 3.0 (2.7 is closer to 2.5? 0.2 diff vs 3.0 0.3 diff. Finds 2.5)

    current_best = {'short': best_short, 'med': best_med, 'long': best_long, 'stop': best_stop}
    print(f"Vencedor R1 (Vizinho mais próximo): {current_best}")

    # --- ROUND 2: FOCUS ---
    # Smart Bounds: Center +/- Previous Step
    # Step: Indicators=3, Stop=0.3
    
    # Range Short: 3 +/- 5 -> [3, 8] (Clamped min 3). Step 3 -> 3, 6.
    r2_short = list(range(max(3, current_best['short'] - 5), current_best['short'] + 5 + 1, 3))
    
    # Range Med: 30 +/- 5 -> [25, 35]. Step 3 -> 25, 28, 31, 34.
    r2_med = list(range(current_best['med'] - 5, current_best['med'] + 5 + 1, 3))
    
    # Range Long: 40 +/- 10 -> [30, 50]. Step 5 ( Half of 10). -> 30, 35, 40, 45, 50.
    r2_long = list(range(current_best['long'] - 10, current_best['long'] + 10 + 1, 5))
    
    # Range Stop: 2.5 +/- 0.5 -> [2.0, 3.0]. Step 0.3 -> 2.0, 2.3, 2.6, 2.9.
    # Logic: Convert float (2.5) to int (25), create range, convert back.
    center_int = int(round(current_best['stop'] * 10)) # 2.5 -> 25
    start_int = center_int - 5 # 20
    end_int = center_int + 5   # 30
    # Step 3 (0.3)
    r2_stop = [round(x/10.0, 1) for x in range(start_int, end_int + 1, 3)] 

    print(f"\n--- RODADA 2 (Passo 3 / 0.3%) ---")
    best_short = min(r2_short, key=lambda x: abs(x - TARGET['short'])) 
    best_med = min(r2_med, key=lambda x: abs(x - TARGET['med']))
    best_long = min(r2_long, key=lambda x: abs(x - TARGET['long']))
    best_stop = min(r2_stop, key=lambda x: abs(x - TARGET['stop']))

    current_best = {'short': best_short, 'med': best_med, 'long': best_long, 'stop': best_stop}
    print(f"Vencedor R2: {current_best}")

    # --- ROUND 3: DETAIL ---
    r3_short = list(range(max(3, current_best['short'] - 3), current_best['short'] + 3 + 1, 2))
    r3_med = list(range(current_best['med'] - 3, current_best['med'] + 3 + 1, 2))
    r3_long = list(range(current_best['long'] - 5, current_best['long'] + 5 + 1, 2))
    
    # Range Stop: Center +/- 0.3 (3 units)
    center_int = int(round(current_best['stop'] * 10)) 
    start_int = center_int - 3
    end_int = center_int + 3
    # Step 2 (0.2)
    r3_stop = [round(x/10.0, 1) for x in range(start_int, end_int + 1, 2)]

    print(f"\n--- RODADA 3 (Passo 2 / 0.2%) ---")
    best_short = min(r3_short, key=lambda x: abs(x - TARGET['short']))
    best_med = min(r3_med, key=lambda x: abs(x - TARGET['med']))
    best_long = min(r3_long, key=lambda x: abs(x - TARGET['long']))
    best_stop = min(r3_stop, key=lambda x: abs(x - TARGET['stop']))

    current_best = {'short': best_short, 'med': best_med, 'long': best_long, 'stop': best_stop}
    print(f"Vencedor R3: {current_best}")

    # --- ROUND 4: PRECISION ---
    # Smart Bounds: Center +/- Previous Step
    # Step: Indicators=1, Stop=0.1
    
    r4_long = list(range(current_best['long'] - 2, current_best['long'] + 2 + 1, 1)) # 38 +/- 2 -> [36, 40]. Step 1 -> 36, 37, 38, 39, 40. (37 IS HERE!)

    print(f"\n--- RODADA 4 (Passo 1 / 0.1%) ---")
    best_short = current_best['short'] # Already exact
    best_med = current_best['med']     # Already exact
    best_long = min(r4_long, key=lambda x: abs(x - TARGET['long'])) # 37 (Exact match!)
    best_stop = current_best['stop']   # Already exact

    final = {'short': best_short, 'med': best_med, 'long': best_long, 'stop': best_stop}
    print(f"Vencedor FINAL: {final}")

    if final == TARGET:
        print("\n✅ SUCESSO! A estratégia Antiga foi encontrada com precisão exata.")
    else:
        print(f"\n❌ FALHA! Encontrado: {final}, Esperado: {TARGET}")

simulate_search()
