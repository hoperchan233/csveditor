import os, pathlib
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from scipy.signal import savgol_filter

# ────────────── ONLY args！！！！ 
IN_CSV      = "fixed/17_red_crop_409.37-450.80.csv"  
FPS         = 30          # Fram BTW care
SG_WINDOW_S = 0.5         # Savitzky-Golay 窗宽（秒）
SG_POLY     = 3           # SavGol 拟合阶数
X_LIM       = (-25, 25)   # 经典rink尺寸捏
Y_LIM       = (-3,  3)
# ──────────────────────────────────────────

COL_TIME, COL_X, COL_Y = 'time', 'x', 'y'
DT = 1 / FPS
win = int(round(SG_WINDOW_S / DT));  win += 1 - win % 2  # 奇数

src = pathlib.Path(IN_CSV)
if not src.exists():
    raise FileNotFoundError(src)


df = pd.read_csv(src, usecols=[COL_TIME, COL_X, COL_Y]).sort_values(COL_TIME)
t0, t1 = df[COL_TIME].iloc[[0, -1]]
print(f"⏱  Length {t1 - t0:.2f}s • {len(df)} frames")

# 固定 FPS
new_times = np.arange(t0, t1 + 1e-9, DT)
full = (pd.DataFrame({COL_TIME: new_times})
          .merge(df, on=COL_TIME, how='left')
          .interpolate('linear'))
print(f"➕ Filled {len(full) - len(df)} missing frames")

# Savitzky–Golay 平滑
for col in (COL_X, COL_Y):
    full[col] = savgol_filter(full[col], window_length=win,
                              polyorder=SG_POLY, mode='interp')
print(f"🧹 SavGol window = {win} frames (~{win*DT:.2f}s)")

# 存盘
out_path = src.with_name(src.stem + '_30fps_smooth.csv')
full.to_csv(out_path, index=False)
print(f"💾 Saved: {out_path}")

# plot一下
fig, ax = plt.subplots()
ax.plot(df[COL_X],  df[COL_Y],  '.', ms=3, alpha=.35, label='Original')
ax.plot(full[COL_X], full[COL_Y], '-', lw=1.2,          label='Smoothed 30 fps')
ax.set_aspect('equal')
if X_LIM: ax.set_xlim(*X_LIM)
if Y_LIM: ax.set_ylim(*Y_LIM)
ax.set_title('Trajectory – original vs. interpolated & smoothed')
ax.legend();  plt.tight_layout();  plt.show()
