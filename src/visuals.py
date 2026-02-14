import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import seaborn as sns
import pandas as pd
import os

def draw_table_with_logos(df_results, filename='data/visualisations/visual_table.png'):
    if df_results.empty:
        return
    
    logos_folder = 'data/logos/'

    df = df_results.copy()

    headers = ['Team', 'Expected\nPoints', 'Top1\n(%)', 'Play-off\n(%)', 'Relegation\n(%)']

    n_rows = len(df)
    height = n_rows * 0.6 + 2
    fig, ax = plt.subplots(figsize=(10, height))

    ax.axis('off')
    ax.set_xlim(0,10)
    ax.set_ylim(-1, n_rows + 1)

    y_pos = n_rows
    col_pos = [0.5, 4.5, 6.5, 8.0, 9.5]

    for idx, header in enumerate(headers):
        ax.text(col_pos[idx], y_pos + 0.5, header,
                weight='bold', fontsize=11, ha='center', va='center')
        
    ax.plot([0,10], [y_pos, y_pos], color='black', linewidth=1)

    for i, row in enumerate(df.itertuples()):
        y = n_rows - 1 - i
        team_code = row.Team

        # Team logo
        logo_path = os.path.join(logos_folder, f"{team_code}.png")

        if os.path.exists(logo_path):
            img = mpimg.imread(logo_path)
            imagebox = OffsetImage(img, zoom=0.2)
            ab = AnnotationBbox(imagebox, (0.5, y), frameon=False, box_alignment=(0.5, 0.5))
            ax.add_artist(ab)
        else:
            ax.text(0.5, y, "●", ha='center', va='center', colors='gray')

        # Team name
        ax.text(1.2, y, team_code, weight='bold', fontsize=12, va='center', ha='left')

        # Stats
        def get_color(value, max_val=100, is_bad=False):
            alpha = value / max_val
            if alpha > 1: alpha = 1
            if is_bad:
                return (1, 0, 0, alpha * 0.7)
            return (0, 0.5, 0, alpha * 0.7)
        
        # Expected points
        ax.text(col_pos[1], y, f"{row.Expected_Points:.1f}", ha='center', va='center', fontsize=11)

        # Top1 probability (green)
        c_win = get_color(row.Win_Probability)
        ax.text(col_pos[2], y, f"{row.Win_Probability:.2f}%", ha='center', va='center',
                bbox=dict(facecolor=c_win, edgecolor='none', pad=3))
        
        # Playoff probability (green/yellow)
        c_po = get_color(row.Playoff_Probability)
        ax.text(col_pos[3], y, f"{row.Playoff_Probability:.2f}%", ha='center', va='center',
                bbox=dict(facecolor=c_po, edgecolor='none', pad=3))
        
        # Relegation probability (red)
        c_rel = get_color(row.Relegation_Probability, is_bad=True)
        ax.text(col_pos[4], y, f"{row.Relegation_Probability:.2f}%", ha='center', va='center',
                bbox=dict(facecolor=c_rel, edgecolor='none', pad=3))
        
        line_y = y - 0.5

        if i == 7:
            ax.plot([0,10], [line_y, line_y], color='green', linewidth=1.5, linestyle='--')
        elif i == n_rows - 3:
            ax.plot([0,10], [line_y, line_y], color='red', linewidth=1.5, linestyle='--')
        elif i < n_rows - 1:
            ax.plot([0, 10], [line_y, line_y], color='gray', linewidth=0.5, alpha=0.3)

    plt.tight_layout()
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Table saved in {filename}")
