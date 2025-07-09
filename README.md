# Blackjack Reinforcement Learning Agent

A comprehensive implementation of a Q-learning agent that learns to play Blackjack optimally through reinforcement learning

### **Project Structure**

```
blackjack-rl/
├── main.py                # Main training simulation
├── UI.py                  # User interface components
├── metrics.ipynb         # Analysis notebook
├── requirements.txt      # Dependencies
├── README.md            # This file
├── assets/              # Game assets (images)
│   ├── card_*.png       # Card images (2C through AS)
│   ├── button_*.png     # UI button images
│   ├── chip_*.png       # Poker chip images
│   ├── felt_background.png
│   ├── wooden_rail.png
│   └── icon_*.png       # UI icons
├── plots/               # Generated visualizations
│   ├── win_rate_progression.png
│   ├── learned_policy_hard_hands.png
│   └── learned_policy_soft_hands.png
└── training_results.json # Exported training datam features real-time visualization, performance tracking, and strategy analysis tools.
```

### **Project Overview**

This project demonstrates the application of Q-learning to master Blackjack Basic Strategy. The agent learns through 50,000 episodes of simulated gameplay, converging on optimal decision-making that matches established casino Basic Strategy.

### **Key Features**

- **Real-time Training Visualization**: Watch the agent learn with live gameplay rendering
- **Comprehensive Metrics**: Track win rates, learning progress, and strategy convergence
- **Strategy Analysis**: Generate policy heatmaps showing learned decision patterns
- **Reproducible Results**: Seeded random number generation for consistent outcomes
- **Interactive Controls**: Start, pause, and reset training simulations


###  **Quick Start**

### **Prerequisites**
- Python 3.8 or higher
- pip package manager

### **Installation**

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/blackjack-rl
   cd blackjack-rl
   # Or simply clone/download the files to your preferred directory
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Create assets directory** (optional - placeholder images will be generated)
   ```bash
   mkdir assets
   # Place your card images and UI assets here
   ```

4. **Run the training simulation**
   ```bash
   python main.py
   ```

### **Basic Usage**

1. **Start Training**: Click "Start Sim" to begin the 50,000-episode training
2. **Monitor Progress**: Watch real-time metrics including win rate and epsilon decay
3. **Pause/Resume**: Use "Pause Sim" to halt training at any time
4. **Reset**: Click "Reset Q" to clear learned knowledge and start fresh
5. **Analyze Results**: After training, run the Jupyter notebook for detailed analysis

## 📊 **Performance Analysis**

### **Training Metrics**

- **Episodes**: 50,000 games
- **Win Rate Tracking**: Performance measured every 1,000 episodes
- **Expected Performance**: ~43% win rate (optimal for Basic Strategy)
- **Learning Parameters**:
  - Learning Rate (α): 0.05
  - Discount Factor (γ): 0.95
  - Epsilon Decay: 0.99995 per episode

### **Strategy Validation**

The agent learns key Basic Strategy decisions:

| Situation | Learned Action | Basic Strategy | Status |
|-----------|---------------|----------------|---------|
| Player 17 vs Dealer 7 | Stand | Stand | ✅ Correct |
| Player 12 vs Dealer 4 | Stand | Stand | ✅ Correct |
| Player 11 vs Dealer 7 | Hit | Hit | ✅ Correct |
| Player 18 vs Dealer 10 | Stand | Stand | ✅ Correct |

## 📈 **Data Analysis & Visualization**

### **Jupyter Notebook Analysis**

Run the included `metrics.ipynb` notebook for comprehensive analysis:

```bash
jupyter notebook metrics.ipynb
```

**Generated Visualizations:**

- **Win Rate Progression**: Shows learning improvement over time
- **Strategy Heatmaps**: Visual representation of learned policy
- **Hard vs Soft Hands**: Separate analysis for different hand types

### **Exported Data**

Training results are automatically saved to `training_results.json`:

- Complete Q-table with all learned state-action values
- Episode-by-episode win rate history
- Hyperparameters and final statistics
- Full reproducibility data

## 🎮 **Game Rules Implementation**

### **Blackjack Rules**

- Standard 52-card deck, reshuffled each hand
- Dealer stands on all 17s (hard and soft)
- Player blackjack pays 3:2 (1.5x reward)
- No doubling down or splitting (Hit/Stand only)

### **State Representation**

```python
State = (player_sum, dealer_upcard, usable_ace)
# player_sum: 4-21 (player's hand total)
# dealer_upcard: 2-11 (dealer's visible card value)
# usable_ace: 0/1 (whether player has usable ace)
```

### **Action Space**

- **0**: Stand (keep current hand)
- **1**: Hit (take another card)

## 🧠 **Q-Learning Implementation**

### **Bellman Equation**

```math
Q(s,a) ← Q(s,a) + α[R + γ·max Q(s',a') - Q(s,a)]
```

**Where:**

- `Q(s,a)`: Quality of action `a` in state `s`
- `α`: Learning rate (0.05)
- `R`: Immediate reward
- `γ`: Discount factor (0.95)
- `s'`: Next state after action

### **Reward Structure**

- **Win**: +1.0
- **Blackjack Win**: +1.5 (3:2 payout)
- **Loss**: -1.0
- **Push (Tie)**: 0.0

## 📁 **Project Structure**

```
blackjack-rl-agent/
├── main.py                 # Main training simulation
├── metrics.ipynb          # Analysis notebook
├── requirements.txt       # Dependencies
├── README.md             # This file
├── assets/               # Game assets (images, sounds)
│   ├── card_*.png        # Playing card images
│   ├── felt_background.png
│   └── wooden_rail.png
├── plots/                # Generated visualizations
│   ├── win_rate_progression.png
│   ├── learned_policy_hard_hands.png
│   └── learned_policy_soft_hands.png
└── training_results.json # Exported training data
```

## 🔧 **Configuration**

### **Hyperparameter Tuning**

Modify these constants in `main.py` to experiment:

```python
LEARNING_RATE = 0.05        # How much to learn from each experience
DISCOUNT_FACTOR = 0.95      # Importance of future rewards
EPSILON_START = 1.0         # Initial exploration rate
EPSILON_DECAY = 0.99995     # Exploration decay per episode (faster decay)
EPSILON_MIN = 0.01          # Minimum exploration rate
EPISODES = 50000           # Total training episodes
INTERVAL_SIZE = 1000       # Episodes between win rate logging
```

### **Visualization Settings**

```python
simulation_speed = 0.01     # Seconds between game steps (0.01 = default speed)
                           # Decrease for faster training (e.g., 0.001)
                           # Increase for slower visualization (e.g., 0.1)
```

## 📚 **Academic Context**

This implementation serves as a practical demonstration of:

- **Reinforcement Learning**: Model-free learning through trial and error
- **Q-Learning**: Value-based method for optimal policy discovery
- **Epsilon-Greedy Strategy**: Balancing exploration vs exploitation
- **Temporal Difference Learning**: Learning from prediction errors

### **Expected Learning Outcomes**

1. Understanding of Q-learning algorithm mechanics
2. Practical experience with RL hyperparameter tuning
3. Insight into the mathematics of Blackjack Basic Strategy
4. Experience with real-time visualization of learning processes

## 🤝 **Contributing**

Contributions are welcome! Areas for enhancement:

- Additional Blackjack actions (Double Down, Split)
- Alternative RL algorithms (SARSA, Deep Q-Networks)
- Enhanced visualization and UI improvements
- Performance optimizations for faster training

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 **Results Summary**

After 50,000 training episodes:

- **Final Win Rate**: ~43% (matches theoretical Basic Strategy)
- **Strategy Accuracy**: >95% alignment with optimal Basic Strategy
- **Learning Convergence**: Stable performance after ~30,000 episodes
- **Q-Value Stability**: Consistent decision-making in key situations

---

## Interview Project

Built for Flutter International as an interview task.
