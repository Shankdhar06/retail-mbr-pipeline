# %% [markdown]
# RETAIL MBR PIPELINE
# 
# Python Layer 2: KPI Chart Builder (with MoM & YoY)

# %%
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
from pathlib import Path

# %%
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / 'data' / 'warehouse' / 'master_kpi_trends.csv'
OUT_PATH  = BASE_DIR / 'output' / 'charts'
OUT_PATH.mkdir(parents=True, exist_ok=True)

# %%
df = pd.read_csv(DATA_PATH)
df['month'] = pd.to_datetime(df['month'])
df = df.sort_values('month')

print(f"✅ Loaded: {df.shape[0]} rows")

# %%
sns.set_theme(style='whitegrid')
plt.rcParams['font.family'] = 'DejaVu Sans'

COLORS = {
    'revenue'    : '#2196F3',
    'pcogs'      : '#F44336',
    'ops'        : '#4CAF50',
    'margin'     : '#FF9800',
    'conversion' : '#9C27B0',
    'positive'   : '#4CAF50',
    'negative'   : '#F44336',
    'neutral'    : '#9E9E9E'
}

# %%
def mom_label(value):
    if pd.isnull(value):
        return 'N/A', COLORS['neutral']
    arrow = '▲' if value >= 0 else '▼'
    color = COLORS['positive'] if value >= 0 else COLORS['negative']
    return f"{arrow} {abs(value):.1f}% MoM", color

def yoy_label(value):
    if pd.isnull(value):
        return 'N/A', COLORS['neutral']
    arrow = '▲' if value >= 0 else '▼'
    color = COLORS['positive'] if value >= 0 else COLORS['negative']
    return f"{arrow} {abs(value):.1f}% YoY", color

# %% [markdown]
# CHART 1: Monthly Revenue Trend + MoM Annotation

# %%
def chart_revenue_trend(df):
    monthly = df.groupby('month').agg(
        revenue          = ('revenue', 'sum'),
        revenue_mom_pct  = ('revenue_mom_pct', 'mean'),
        revenue_yoy_pct  = ('revenue_yoy_pct', 'mean')
    ).reset_index()

    # Get latest month stats
    latest       = monthly.iloc[-1]
    mom_text, mom_color = mom_label(latest['revenue_mom_pct'])
    yoy_text, yoy_color = yoy_label(latest['revenue_yoy_pct'])

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(monthly['month'], monthly['revenue'],
            marker='o', linewidth=2.5,
            color=COLORS['revenue'], markersize=5)
    ax.fill_between(monthly['month'], monthly['revenue'],
                    alpha=0.08, color=COLORS['revenue'])

    # MoM & YoY annotation box
    ax.annotate(
        f"Latest Month\nRevenue: ${latest['revenue']:,.0f}\n{mom_text}\n{yoy_text}",
        xy=(monthly['month'].iloc[-1], latest['revenue']),
        xytext=(-120, -60),
        textcoords='offset points',
        fontsize=9,
        bbox=dict(boxstyle='round,pad=0.5', fc='white', ec='#2196F3', lw=1.5),
        arrowprops=dict(arrowstyle='->', color='#2196F3')
    )

    ax.set_title('Monthly Revenue Trend', fontsize=16,
                 fontweight='bold', pad=15)
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Revenue ($)', fontsize=12)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f'${x:,.0f}'))
    ax.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    path = OUT_PATH / 'chart1_revenue_trend.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ Chart 1 saved: {path}")

# %% [markdown]
# CHART 2: OPS vs Revenue vs PCOGS by Category with MoM badge per KPI

# %%
def chart_kpi_by_category(df):
    cat = df.groupby('category').agg(
        revenue         = ('revenue', 'sum'),
        pcogs           = ('pcogs', 'sum'),
        ops             = ('ops', 'sum'),
        rev_mom         = ('revenue_mom_pct', 'mean'),
        pcogs_mom       = ('pcogs_mom_pct', 'mean'),
        ops_mom         = ('ops_mom_pct', 'mean')
    ).reset_index()

    x     = np.arange(len(cat))
    width = 0.25

    fig, ax = plt.subplots(figsize=(13, 7))
    b1 = ax.bar(x - width, cat['ops'],
                width, label='OPS',     color=COLORS['ops'],     alpha=0.85)
    b2 = ax.bar(x,         cat['revenue'],
                width, label='Revenue', color=COLORS['revenue'], alpha=0.85)
    b3 = ax.bar(x + width, cat['pcogs'],
                width, label='PCOGS',   color=COLORS['pcogs'],   alpha=0.85)

    # MoM badges above each group
    for i, row in cat.iterrows():
        for val, xpos, col in [
            (row['ops_mom'],   x[i] - width, COLORS['ops']),
            (row['rev_mom'],   x[i],         COLORS['revenue']),
            (row['pcogs_mom'], x[i] + width, COLORS['pcogs'])
        ]:
            text, color = mom_label(val)
            ax.text(xpos, max(row['ops'], row['revenue'], row['pcogs']) * 1.03,
                    text, ha='center', fontsize=7.5,
                    color=color, fontweight='bold')

    ax.set_title('OPS vs Revenue vs PCOGS by Category',
                 fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Category', fontsize=12)
    ax.set_ylabel('Value ($)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(cat['category'], fontsize=11)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f'${x:,.0f}'))
    ax.legend(fontsize=11)

    plt.tight_layout()
    path = OUT_PATH / 'chart2_kpi_by_category.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ Chart 2 saved: {path}")

# %% [markdown]
# CHART 3: Profit Margin % by Region with MoM & YoY change

# %%
def chart_margin_by_region(df):
    region = df.groupby('region').apply(
        lambda x: pd.Series({
            'profit_margin_pct' : round(x['profit_margin_pct'].mean(), 2),
            'margin_mom_change' : round(x['margin_mom_change'].mean(), 2),
            'margin_yoy_change' : round(x['margin_yoy_change'].mean(), 2)
        })
    ).reset_index().sort_values('profit_margin_pct', ascending=True)

    fig, ax = plt.subplots(figsize=(11, 6))
    bar_colors = [COLORS['positive'] if v >= 0 else COLORS['negative']
                  for v in region['margin_mom_change']]
    bars = ax.barh(region['region'], region['profit_margin_pct'],
                   color=bar_colors, alpha=0.85)

    for bar, row in zip(bars, region.itertuples()):
        mom_t, mom_c = mom_label(row.margin_mom_change)
        yoy_t, yoy_c = yoy_label(row.margin_yoy_change)
        ax.text(bar.get_width() + 0.2,
                bar.get_y() + bar.get_height() * 0.7,
                f'{row.profit_margin_pct}%',
                va='center', fontsize=11, fontweight='bold')
        ax.text(bar.get_width() + 0.2,
                bar.get_y() + bar.get_height() * 0.2,
                f'{mom_t}  |  {yoy_t}',
                va='center', fontsize=8, color=COLORS['neutral'])

    ax.set_title('Profit Margin % by Region (with MoM & YoY)',
                 fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Profit Margin %', fontsize=12)
    ax.set_xlim(0, region['profit_margin_pct'].max() + 8)

    plt.tight_layout()
    path = OUT_PATH / 'chart3_margin_by_region.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ Chart 3 saved: {path}")

# %% [markdown]
# CHART 4: Conversion Rate by Segment with MoM change

# %%
def chart_conversion_by_segment(df):
    seg = df.groupby('segment').apply(
        lambda x: pd.Series({
            'conversion_rate'       : round(x['conversion_rate'].mean(), 2),
            'conversion_mom_change' : round(x['conversion_mom_change'].mean(), 2),
            'conversion_yoy_change' : round(x['conversion_yoy_change'].mean(), 2)
        })
    ).reset_index().sort_values('conversion_rate', ascending=False)

    fig, ax = plt.subplots(figsize=(11, 6))
    bars = ax.bar(seg['segment'], seg['conversion_rate'],
                  color=COLORS['conversion'], width=0.45, alpha=0.85)

    for bar, row in zip(bars, seg.itertuples()):
        mom_t, mom_c = mom_label(row.conversion_mom_change)
        yoy_t, yoy_c = yoy_label(row.conversion_yoy_change)
        # Main value
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.4,
                f'{row.conversion_rate}%',
                ha='center', fontsize=12, fontweight='bold')
        # MoM
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 1.8,
                mom_t, ha='center', fontsize=8,
                color=mom_c, fontweight='bold')
        # YoY
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 3.2,
                yoy_t, ha='center', fontsize=8,
                color=yoy_c, fontweight='bold')

    ax.set_title('Conversion Rate by Customer Segment',
                 fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Segment', fontsize=12)
    ax.set_ylabel('Conversion Rate %', fontsize=12)
    ax.set_ylim(0, seg['conversion_rate'].max() + 10)

    plt.tight_layout()
    path = OUT_PATH / 'chart4_conversion_by_segment.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ Chart 4 saved: {path}")

# %% [markdown]
# CHART 5: Monthly Profit Margin % Trend with YoY comparison overlay

# %%
def chart_margin_trend(df):
    monthly = df.groupby(['year', 'month']).agg(
        profit_margin_pct  = ('profit_margin_pct', 'mean'),
        margin_mom_change  = ('margin_mom_change', 'mean'),
        margin_yoy_change  = ('margin_yoy_change', 'mean')
    ).reset_index()

    # Split by year for YoY overlay
    years = sorted(monthly['year'].unique())

    fig, ax = plt.subplots(figsize=(14, 6))

    for i, year in enumerate(years):
        yr_data = monthly[monthly['year'] == year]
        alpha   = 0.3 if year < max(years) else 1.0
        lw      = 1.2 if year < max(years) else 2.5
        ax.plot(yr_data['month'], yr_data['profit_margin_pct'],
                marker='o', markersize=4,
                linewidth=lw, alpha=alpha,
                label=str(year), color=COLORS['margin'])

    # Average line
    avg = monthly['profit_margin_pct'].mean()
    ax.axhline(y=avg, color='red', linestyle='--',
               linewidth=1.5, label=f'Overall Avg: {avg:.1f}%')

    ax.set_title('Monthly Profit Margin % Trend (YoY Overlay)',
                 fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Profit Margin %', fontsize=12)
    ax.tick_params(axis='x', rotation=45)
    ax.legend(fontsize=10)

    plt.tight_layout()
    path = OUT_PATH / 'chart5_margin_trend.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ Chart 5 saved: {path}")

# %% [markdown]
# KPI Summary Scorecard - Shows all 5 KPIs with MoM & YoY in one view

# %%
def chart_kpi_scorecard(df):
    # Get latest month data
    latest_month = df['month'].max()
    prev_month   = df[df['month'] < latest_month]['month'].max()

    curr = df[df['month'] == latest_month].agg({
        'revenue'           : 'sum',
        'pcogs'             : 'sum',
        'ops'               : 'sum',
        'profit_margin_pct' : 'mean',
        'conversion_rate'   : 'mean',
        'revenue_mom_pct'   : 'mean',
        'revenue_yoy_pct'   : 'mean',
        'pcogs_mom_pct'     : 'mean',
        'pcogs_yoy_pct'     : 'mean',
        'ops_mom_pct'       : 'mean',
        'ops_yoy_pct'       : 'mean',
        'margin_mom_change' : 'mean',
        'margin_yoy_change' : 'mean',
        'conversion_mom_change' : 'mean',
        'conversion_yoy_change' : 'mean'
    })

    kpis = [
        {
            'name'    : 'Revenue',
            'value'   : f"${curr['revenue']:,.0f}",
            'mom'     : curr['revenue_mom_pct'],
            'yoy'     : curr['revenue_yoy_pct'],
            'type'    : 'pct',
            'color'   : COLORS['revenue']
        },
        {
            'name'    : 'PCOGS',
            'value'   : f"${curr['pcogs']:,.0f}",
            'mom'     : curr['pcogs_mom_pct'],
            'yoy'     : curr['pcogs_yoy_pct'],
            'type'    : 'pct',
            'color'   : COLORS['pcogs']
        },
        {
            'name'    : 'OPS',
            'value'   : f"${curr['ops']:,.0f}",
            'mom'     : curr['ops_mom_pct'],
            'yoy'     : curr['ops_yoy_pct'],
            'type'    : 'pct',
            'color'   : COLORS['ops']
        },
        {
            'name'    : 'Profit Margin %',
            'value'   : f"{curr['profit_margin_pct']:.1f}%",
            'mom'     : curr['margin_mom_change'],
            'yoy'     : curr['margin_yoy_change'],
            'type'    : 'pp',
            'color'   : COLORS['margin']
        },
        {
            'name'    : 'Conversion Rate',
            'value'   : f"{curr['conversion_rate']:.1f}%",
            'mom'     : curr['conversion_mom_change'],
            'yoy'     : curr['conversion_yoy_change'],
            'type'    : 'pp',
            'color'   : COLORS['conversion']
        }
    ]

    fig, axes = plt.subplots(1, 5, figsize=(18, 4))
    fig.suptitle(
        f'KPI Scorecard — {pd.to_datetime(latest_month).strftime("%B %Y")}',
        fontsize=16, fontweight='bold', y=1.02
    )

    for ax, kpi in zip(axes, kpis):
        ax.set_facecolor('#F8F9FA')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        # Coloured top border
        ax.add_patch(mpatches.FancyBboxPatch(
            (0, 0), 1, 1,
            boxstyle='round,pad=0.02',
            linewidth=3, edgecolor=kpi['color'],
            facecolor='#F8F9FA'
        ))

        # KPI Name
        ax.text(0.5, 0.85, kpi['name'],
                ha='center', va='center',
                fontsize=11, fontweight='bold',
                color='#424242')

        # KPI Value
        ax.text(0.5, 0.60, kpi['value'],
                ha='center', va='center',
                fontsize=18, fontweight='bold',
                color=kpi['color'])

        # MoM
        mom_t, mom_c = mom_label(kpi['mom'])
        suffix = 'pp' if kpi['type'] == 'pp' else ''
        ax.text(0.5, 0.35,
                f"MoM: {mom_t}{suffix}",
                ha='center', va='center',
                fontsize=9, color=mom_c,
                fontweight='bold')

        # YoY
        yoy_t, yoy_c = yoy_label(kpi['yoy'])
        ax.text(0.5, 0.15,
                f"YoY: {yoy_t}{suffix}",
                ha='center', va='center',
                fontsize=9, color=yoy_c,
                fontweight='bold')

    plt.tight_layout()
    path = OUT_PATH / 'chart6_kpi_scorecard.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ Chart 6 saved: {path}")

# %%
if __name__ == '__main__':
    print("\n📊 Building KPI Charts...\n")
    chart_revenue_trend(df)
    chart_kpi_by_category(df)
    chart_margin_by_region(df)
    chart_conversion_by_segment(df)
    chart_margin_trend(df)
    chart_kpi_scorecard(df)
    print(f"\n🎉 All 6 charts saved to: {OUT_PATH}")

# %%



