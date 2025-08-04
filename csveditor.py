import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import RangeSlider

CSV_PATH  = 'del/9_red.csv'    
TIME_COL  = 'time'
X_COL, Y_COL = 'x', 'y'

# ── load CSV
df = pd.read_csv(CSV_PATH, usecols=[TIME_COL, X_COL, Y_COL])

# ── 初始图 
fig, ax = plt.subplots()
scat = ax.scatter(df[X_COL], df[Y_COL], s=6, c='tab:blue')

# 固定坐标轴范围  
ax.set_xlim(-25, 25)
ax.set_ylim(-3, 3)

ax.set_aspect('equal')
ax.set_title('Drag time-range slider – press S to save')   # fuck font

# 时间滑块 
t_min, t_max = df[TIME_COL].min(), df[TIME_COL].max()
slider_ax = plt.axes([0.15, 0.03, 0.7, 0.04])
slider = RangeSlider(slider_ax, 'Time [s]',
                     valmin=t_min, valmax=t_max,
                     valinit=(t_min, t_max),
                     valstep=(df[TIME_COL].iloc[1] - df[TIME_COL].iloc[0]))

def update(val):
    t_start, t_end = slider.val
    cropped = df.query(f"{TIME_COL}>=@t_start & {TIME_COL}<=@t_end")
    scat.set_offsets(cropped[[X_COL, Y_COL]].values)
    ax.set_title(f'Time {t_start:.2f}–{t_end:.2f} s  (N={len(cropped)})')  
    fig.canvas.draw_idle()

slider.on_changed(update)

# 存盘 
def on_key(event):
    if event.key.lower() == 's':
        t_start, t_end = slider.val
        out = df.query(f"{TIME_COL}>={t_start} & {TIME_COL}<={t_end}")
        out_path = CSV_PATH.replace('.csv',
                                    f'_crop_{t_start:.2f}-{t_end:.2f}.csv')
        out.to_csv(out_path, index=False)
        print(f'✔ Saved to {out_path}')

fig.canvas.mpl_connect('key_press_event', on_key)

plt.show()
