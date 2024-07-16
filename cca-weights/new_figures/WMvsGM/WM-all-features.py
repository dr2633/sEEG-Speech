import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

base_path = '/Users/derekrosenzweig/PycharmProjects/CCA-reduce'

# Directory to save figures
fig_dir = f'{base_path}/cca-weights/new_figures/WMvsGM'
os.makedirs(fig_dir, exist_ok=True)

# Directory containing the CSV files
csv_dir = f'{base_path}/cca-weights/weights'

# List of frequency bands
freqs = ['70-150Hz']

# List of files and titles
files_and_titles = [
    ('EMBEDDING_1', 'GPT-2 PC1'),
    ('EMBEDDING_2', 'GPT-2 PC2'),
    ('EMBEDDING_3', 'GPT-2 PC3'),
    ('EMBEDDING_4', 'GPT-2 PC4'),
    ('EMBEDDING_5', 'GPT-2 PC5'),
    ('ENTROPY', 'GPT-2 Entropy'),
    ('F0', 'Fundamental Frequency'),
    ('INTENSITY', 'Sound Intensity')
]

# Function to create the WM vs GM comparison plot for all electrodes
def create_wm_gm_comparison_plot(df, feature, title, output_path):
    if df.empty:
        print(f"No electrodes found for {feature}")
        return

    print(f"Found {len(df)} electrodes for {feature}")

    # Use absolute values of the weights
    df['abs_weight'] = df['weight'].abs()

    # Create the plot
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='WMvsGM', y='abs_weight', data=df, palette='Set2')
    sns.stripplot(x='WMvsGM', y='abs_weight', data=df, color='black', alpha=0.5, jitter=True)

    # Plot formatting
    plt.title(f'{title} - Electrode Weights WM vs GM', fontsize=16)
    plt.xlabel('WM vs GM', fontsize=12)
    plt.ylabel('Absolute CCA Weights', fontsize=12)

    # Save the plot
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

# Function to create the WM comparison plot across all features
def create_wm_comparison_plot(all_features_df, output_path):
    if all_features_df.empty:
        print(f"No WM electrodes found for any feature")
        return

    # Create the plot
    plt.figure(figsize=(14, 8))
    sns.boxplot(x='Feature', y='abs_weight', data=all_features_df, palette='Set3')
    sns.stripplot(x='Feature', y='abs_weight', data=all_features_df, color='black', alpha=0.5, jitter=True)

    # Plot formatting
    plt.title('WM Electrode Weights Across All Features', fontsize=16)
    plt.xlabel('Feature', fontsize=12)
    plt.ylabel('Absolute CCA Weights', fontsize=12)

    # Save the plot
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

# DataFrame to store WM electrode data across all features
all_features_wm_df = pd.DataFrame()

# Loop through frequency bands
for freq in freqs:
    # Loop through files and create plots
    for input_name, title in files_and_titles:
        file_path = f'{csv_dir}/{freq}_CCA_weights_{input_name}.csv'
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            output_path = os.path.join(fig_dir, f'{freq}_CCA_weights_{input_name}_wm_vs_gm.png')
            create_wm_gm_comparison_plot(df, input_name, title, output_path)

            # Filter for WM electrodes and add feature information
            wm_df = df[df['WMvsGM'] == 'WM'].copy()
            wm_df['Feature'] = title
            all_features_wm_df = pd.concat([all_features_wm_df, wm_df], axis=0)

        else:
            print(f"File not found: {file_path}")

# Create and save the WM comparison plot across all features
output_path_all_features = os.path.join(fig_dir, 'WM_electrodes_across_all_features.png')
create_wm_comparison_plot(all_features_wm_df, output_path_all_features)
