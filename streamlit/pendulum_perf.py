import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import time
import hashlib

# Set page config
st.set_page_config(page_title="Driven Pendulum Trajectories", layout="wide")

# Initialize session state for performance optimization
if 'last_computation_time' not in st.session_state:
    st.session_state.last_computation_time = 0
if 'cached_trajectories' not in st.session_state:
    st.session_state.cached_trajectories = None
if 'cached_params_hash' not in st.session_state:
    st.session_state.cached_params_hash = None

# Title and description
st.title("Driven Pendulum Trajectories")
st.markdown("Visualize solutions to the driven pendulum equation: x''(t) = -sin(x(t)) + ε sin(t)")

# Sidebar controls
st.sidebar.header("Parameters")

# Sliders for parameters with optimized defaults
num_trajectories = st.sidebar.slider("Number of trajectories", min_value=1, max_value=5000, value=8, step=1,
                                    help="Reduced max for better performance")
epsilon = st.sidebar.slider("Driving amplitude (ε)", min_value=0.0, max_value=2.0, value=0.5, step=0.1,
                           help="Larger steps for smoother interaction")
max_time = st.sidebar.slider("Maximum time", min_value=5.0, max_value=50.0, value=15.0, step=2.5,
                            help="Reduced range with larger steps")

st.sidebar.markdown("---")
st.sidebar.header("Visualization Settings")

linewidth = st.sidebar.slider("Line width", min_value=0.5, max_value=2.5, value=1.0, step=0.25)
alpha = st.sidebar.slider("Transparency (α)", min_value=0.3, max_value=1.0, value=0.7, step=0.1)

# Performance settings (collapsible)
with st.sidebar.expander("⚡ Performance Settings"):
    auto_compute = st.checkbox("Auto-compute on change", value=True, 
                              help="Uncheck for manual control")
    computation_quality = st.selectbox("Computation quality", 
                                     ["Fast", "Balanced", "High"], 
                                     index=1,
                                     help="Trade-off between speed and accuracy")

# Define quality settings
quality_settings = {
    "Fast": {"rtol": 1e-6, "points_per_unit": 20, "method": 'RK23'},
    "Balanced": {"rtol": 1e-7, "points_per_unit": 30, "method": 'RK45'},
    "High": {"rtol": 1e-8, "points_per_unit": 50, "method": 'DOP853'}
}

current_quality = quality_settings[computation_quality]

# Create parameter hash for intelligent caching
def create_params_hash(num_traj, eps, max_t, quality):
    """Create hash of parameters for caching"""
    params_str = f"{num_traj}_{eps:.2f}_{max_t:.1f}_{quality}"
    return hashlib.md5(params_str.encode()).hexdigest()

# Define the differential equation system
def driven_pendulum(t, y, epsilon):
    """Optimized driven pendulum equation"""
    x, x_dot = y
    return [x_dot, -np.sin(x) + epsilon * np.cos(t)]

# Optimized initial conditions generation
@st.cache_data(ttl=3600)  # Cache for 1 hour
def generate_initial_conditions_optimized(num_trajectories):
    """Generate optimized initial conditions"""
    if num_trajectories <= 1:
        return [[0.1, 0.1]]
    
    # Use golden ratio for better distribution
    golden_ratio = (1 + np.sqrt(5)) / 2
    angles = np.linspace(0, 2 * np.pi, num_trajectories, endpoint=False)
    
    # Create spiral distribution in phase space
    positions = 2 * np.pi * (np.arange(num_trajectories) / golden_ratio) % (2 * np.pi) - np.pi
    velocities = 3 * np.sin(angles * golden_ratio)
    
    return list(zip(positions, velocities))

# Optimized trajectory solver with chunked computation
@st.cache_data(ttl=1800, show_spinner=False)  # Cache for 30 minutes
def solve_trajectories_optimized(num_trajectories, epsilon, max_time, quality_key):
    """Solve trajectories with optimized parameters"""
    quality = quality_settings[quality_key]
    initial_conditions = generate_initial_conditions_optimized(num_trajectories)
    
    # Optimized time evaluation
    t_span = (0, max_time)
    num_points = max(50, int(max_time * quality["points_per_unit"]))
    t_eval = np.linspace(0, max_time, num_points)
    
    trajectories = []
    
    # Process in smaller chunks for better memory management
    chunk_size = min(10, num_trajectories)
    
    for chunk_start in range(0, num_trajectories, chunk_size):
        chunk_end = min(chunk_start + chunk_size, num_trajectories)
        chunk_ics = initial_conditions[chunk_start:chunk_end]
        
        for i, y0 in enumerate(chunk_ics):
            try:
                sol = solve_ivp(
                    driven_pendulum, t_span, y0, t_eval=t_eval,
                    args=(epsilon,), 
                    method=quality["method"], 
                    rtol=quality["rtol"],
                    max_step=max_time/100  # Prevent too large steps
                )
                
                if sol.success and len(sol.t) > 10:  # Ensure minimum quality
                    trajectories.append({
                        't': sol.t,
                        'x': sol.y[0],
                        'v': sol.y[1],
                        'initial': y0
                    })
            except Exception:
                continue  # Skip failed trajectories silently
    
    return trajectories

# Smart computation with debouncing
def should_recompute():
    """Determine if recomputation is needed based on timing and parameter changes"""
    current_time = time.time()
    params_hash = create_params_hash(num_trajectories, epsilon, max_time, computation_quality)
    
    # Check if parameters changed
    params_changed = st.session_state.cached_params_hash != params_hash
    
    # Debouncing: wait at least 0.5 seconds between computations
    time_elapsed = current_time - st.session_state.last_computation_time
    
    return params_changed and (time_elapsed > 0.5 or not auto_compute)

# Manual compute button for non-auto mode
if not auto_compute:
    compute_button = st.sidebar.button("🔄 Compute Trajectories", type="primary")
    should_compute = compute_button
else:
    should_compute = should_recompute()

# Compute trajectories intelligently
trajectories = None

if should_compute or st.session_state.cached_trajectories is None:
    with st.spinner(f"Computing {num_trajectories} trajectories ({computation_quality} quality)..."):
        try:
            trajectories = solve_trajectories_optimized(
                num_trajectories, epsilon, max_time, computation_quality
            )
            
            # Update cache
            st.session_state.cached_trajectories = trajectories
            st.session_state.cached_params_hash = create_params_hash(
                num_trajectories, epsilon, max_time, computation_quality
            )
            st.session_state.last_computation_time = time.time()
            
        except Exception as e:
            st.error(f"Computation failed: {str(e)}")
            trajectories = []
else:
    # Use cached results
    trajectories = st.session_state.cached_trajectories

# Display results only if we have trajectories
if trajectories:
    # Optimized plotting with reduced complexity for large datasets
    @st.cache_data(ttl=600, show_spinner=False)  # Cache plots for 10 minutes
    def create_optimized_plots(traj_data, linewidth, alpha, max_trajectories=30):
        """Create optimized matplotlib plots"""
        # Limit trajectories for performance
        display_trajectories = traj_data[:max_trajectories]
        
        fig, ax2 = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor('white')
        
        # Optimized color generation
        n_traj = len(display_trajectories)
        colors = plt.cm.viridis(np.linspace(0.1, 0.9, n_traj))
        
        # Plot with reduced line complexity for performance
        for i, traj in enumerate(display_trajectories):
            # Downsample for very long trajectories
            if len(traj['t']) > 1000:
                step = len(traj['t']) // 1000
                t_plot = traj['t'][::step]
                x_plot = traj['x'][::step]
                v_plot = traj['v'][::step]
            else:
                t_plot = traj['t']
                x_plot = traj['x']
                v_plot = traj['v']
                        
            # Phase portrait
            ax2.plot(x_plot, v_plot, color=colors[i], 
                    linewidth=linewidth, alpha=alpha, rasterized=True)
            ax2.scatter(traj['initial'][0], traj['initial'][1], 
                       color=colors[i], s=5, alpha=min(0.8, alpha+0.2), zorder=5)
        
        # Styling
        for ax, title, xlabel, ylabel in [
            (ax2, 'Phase Portrait', 'Position x(t)', 'Velocity x\'(t)')
        ]:
            ax.set_title(title, fontsize=13, color='#333', pad=10)
            ax.set_xlabel(xlabel, fontsize=11, color='#333')
            ax.set_ylabel(ylabel, fontsize=11, color='#333')
            ax.grid(True, alpha=0.25, linewidth=0.5)
            ax.set_facecolor('#fafafa')
            
            for spine in ax.spines.values():
                spine.set_color('#666')
            ax.tick_params(colors='#666', labelsize=9)
        
        plt.tight_layout(pad=2)
        return fig
    
    # Create and display plots
    try:
        plot_key = f"{len(trajectories)}_{linewidth}_{alpha}_{id(trajectories)}"
        fig = create_optimized_plots(trajectories, linewidth, alpha)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)  # Prevent memory leaks
        
    except Exception as e:
        st.error(f"Plotting failed: {str(e)}")
    
    # Optimized metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Trajectories", len(trajectories))
        st.metric("Quality", computation_quality)
    
    with col2:
        st.metric("Driving (ε)", f"{epsilon:.2f}")
        st.metric("Time Range", f"0-{max_time:.0f}")
    
    with col3:
        st.metric("Avg Points/Traj", f"{int(np.mean([len(t['t']) for t in trajectories]))}")
        st.metric("Cache Status", "✅ Cached" if not should_compute else "🔄 Fresh")
    
    with col4:
        if trajectories:
            final_positions = [t['x'][-1] for t in trajectories]
            st.metric("Position Range", f"{np.ptp(final_positions):.2f}")
            computation_time = time.time() - st.session_state.last_computation_time
            st.metric("Last Compute", f"{computation_time:.1f}s ago")

else:
    st.warning("No trajectories computed. Adjust parameters or click 'Compute Trajectories'.")
