import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba

# Set page config
st.set_page_config(page_title="Time Series Grid Visualization", layout="wide")

# Title and description
st.title("Time Series Grid Visualization")
st.markdown("Generate and visualize multiple cumulative time series in a grid layout")

# Sidebar controls
st.sidebar.header("Parameters")

# Sliders for main parameters
n = st.sidebar.slider("Number of rows (n)", min_value=1, max_value=10, value=3, step=1)
p = st.sidebar.slider("Number of columns (p)", min_value=1, max_value=10, value=4, step=1)
T = st.sidebar.slider("Time series length (T)", min_value=1000, max_value=100000, value=50000, step=1000)

st.sidebar.markdown("---")
st.sidebar.header("Visualization Settings")

# Sliders for visualization parameters
linewidth = st.sidebar.slider("Line width", min_value=0.0, max_value=5.0, value=1.5, step=0.1)
alpha = st.sidebar.slider("Transparency (alpha)", min_value=0.0, max_value=1.0, value=0.8, step=0.05)

# Generate time series data
@st.cache_data
def generate_time_series(n, p, T, seed=42):
    """Generate n*p time series of length T using cumsum of normal random variables"""
    np.random.seed(seed)
    time_series = []
    
    for i in range(n):
        row_series = []
        for j in range(p):
            # Generate random walk (cumsum of normal variables)
            random_increments = np.random.normal(0, 1, T)
            cumulative_series = np.cumsum(random_increments)
            row_series.append(cumulative_series)
        time_series.append(row_series)
    
    return time_series

# Generate the data
time_series_data = generate_time_series(n, p, T)

# Create the plot
fig, axes = plt.subplots(n, p, figsize=(15, 3*n))

# Handle single subplot case
if n == 1 and p == 1:
    axes = [[axes]]
elif n == 1:
    axes = [axes]
elif p == 1:
    axes = [[ax] for ax in axes]

# Set the style
plt.style.use('default')
fig.patch.set_facecolor('white')

# Plot each time series
for i in range(n):
    for j in range(p):
        ax = axes[i][j]
        
        # Calculate color based on position
        color_intensity = (i * j) / (n * p) if n * p > 0 else 0
        color = plt.cm.viridis(color_intensity)
        
        # Plot the time series
        time_points = np.arange(T)
        ax.plot(time_points, time_series_data[i][j], 
               color=color, linewidth=linewidth, alpha=alpha)
        
        # Styling for sober appearance
        ax.grid(True, alpha=0.3, linewidth=0.5)
        ax.set_facecolor('#fafafa')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#666666')
        ax.spines['bottom'].set_color('#666666')
        ax.tick_params(colors='#666666', labelsize=8)
        
        # Set title for each subplot
        ax.set_title(f'Series ({i+1},{j+1})', fontsize=10, color='#333333', pad=8)
        
        # Only show x-label on bottom row
        if i == n - 1:
            ax.set_xlabel('Time', fontsize=9, color='#666666')
        
        # Only show y-label on leftmost column
        if j == 0:
            ax.set_ylabel('Cumulative Value', fontsize=9, color='#666666')

# Adjust layout
plt.tight_layout(pad=2.0)

# Display the plot
st.pyplot(fig)