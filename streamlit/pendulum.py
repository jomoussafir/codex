import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Set page config
st.set_page_config(page_title="Driven Pendulum Trajectories", layout="wide")

# Title and description
st.title("Driven Pendulum Trajectories")
st.markdown("Visualize solutions to the driven pendulum equation: x''(t) = -sin(x(t)) + ε sin(t)")

# Sidebar controls
st.sidebar.header("Parameters")

# Sliders for parameters
num_trajectories = st.sidebar.slider("Number of trajectories", min_value=1, max_value=100, value=10, step=1)
epsilon = st.sidebar.slider("Driving amplitude (ε)", min_value=0.0, max_value=2.0, value=0.5, step=0.05)
max_time = st.sidebar.slider("Maximum time", min_value=.1, max_value=10.0, value=1.0, step=.1)

st.sidebar.markdown("---")
st.sidebar.header("Visualization Settings")

# Additional visualization controls
linewidth = st.sidebar.slider("Line width", min_value=0.1, max_value=3.0, value=0.8, step=0.1)
alpha = st.sidebar.slider("Transparency (α)", min_value=0.1, max_value=1.0, value=0.7, step=0.05)

# Define the differential equation system
def driven_pendulum(t, y, epsilon):
    """
    Driven pendulum equation: x'' = -sin(x) + epsilon * sin(t)
    State vector y = [x, x']
    Returns dy/dt = [x', -sin(x) + epsilon * sin(t)]
    """
    x, x_dot = y
    return [x_dot, -np.sin(x) + epsilon * np.sin(t)]

# Generate initial conditions
@st.cache_data
def generate_initial_conditions(num_trajectories, seed=42):
    """Generate diverse initial conditions for the trajectories"""
    np.random.seed(seed)
    
    # Mix of systematic and random initial conditions
    if num_trajectories <= 20:
        # For small numbers, use a systematic grid
        x0_range = np.linspace(-np.pi, np.pi, int(np.sqrt(num_trajectories)) + 1)
        v0_range = np.linspace(-2, 2, int(np.sqrt(num_trajectories)) + 1)
        initial_conditions = []
        
        for x0 in x0_range:
            for v0 in v0_range:
                initial_conditions.append([x0, v0])
                if len(initial_conditions) >= num_trajectories:
                    break
            if len(initial_conditions) >= num_trajectories:
                break
    else:
        # For larger numbers, use random sampling
        x0_vals = np.random.uniform(-np.pi, np.pi, num_trajectories)
        v0_vals = np.random.uniform(-3, 3, num_trajectories)
        initial_conditions = list(zip(x0_vals, v0_vals))
    
    return initial_conditions[:num_trajectories]

# Solve the differential equation
@st.cache_data
def solve_trajectories(num_trajectories, epsilon, max_time):
    """Solve the differential equation for multiple initial conditions"""
    initial_conditions = generate_initial_conditions(num_trajectories)
    
    # Time points
    t_span = (0, max_time)
    t_eval = np.linspace(0, max_time, int(max_time * 50))  # 50 points per unit time
    
    trajectories = []
    
    for i, y0 in enumerate(initial_conditions):
        try:
            # Solve the ODE
            sol = solve_ivp(driven_pendulum, t_span, y0, t_eval=t_eval, 
                          args=(epsilon,), method='RK45', rtol=1e-8)
            
            if sol.success:
                trajectories.append({
                    't': sol.t,
                    'x': sol.y[0],
                    'v': sol.y[1],
                    'initial': y0
                })
        except:
            # Skip problematic trajectories
            continue
    
    return trajectories

# Generate solutions
with st.spinner("Computing trajectories..."):
    trajectories = solve_trajectories(num_trajectories, epsilon, max_time)

# Create the plots
fig, ax2 = plt.subplots(figsize=(8, 5))

# Set the style
plt.style.use('default')
fig.patch.set_facecolor('white')

# Color scheme
colors = plt.cm.viridis(np.linspace(0, 1, len(trajectories)))

# Plot 2: Phase Portrait (velocity vs position)
for i, traj in enumerate(trajectories):
    ax2.plot(traj['x'], traj['v'], color=colors[i], 
             linewidth=linewidth, alpha=alpha)
    
    # Mark initial conditions
    ax2.scatter(traj['initial'][0], traj['initial'][1], 
               color=colors[i], s=2, alpha=0.8, zorder=5)

ax2.set_xlabel('Position x(t)', fontsize=12, color='#333333')
ax2.set_ylabel('Velocity x\'(t)', fontsize=12, color='#333333')
ax2.set_title('Phase Portrait', fontsize=14, color='#333333', pad=15)
ax2.grid(True, alpha=0.3, linewidth=0.5)
ax2.set_facecolor('#fafafa')

# Styling
for spine in ax2.spines.values():
    spine.set_color('#666666')
ax2.tick_params(colors='#666666')

# Adjust layout
plt.tight_layout(pad=3.0)

# Display the plot
st.pyplot(fig)
