import mne
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_score, KFold
import os
import csv

# Set parameters for the concatenated file path
freq = '70-150Hz'
pro = 'phoneme_epochs'
features = ('phonation', 'manner', 'place')

# List all sessions, stimuli, and runs to loop through
stimuli = ['Jobs1', 'Jobs2', 'Jobs3', 'AttFast', 'AttSlow', 'BecFast', 'BecSlow', 'CampFast', 'CampSlow']
runs = ['run-01', 'run-02']

# Set base path depending on who is running the code
user_paths = ['/Users/derekrosenzweig/Documents/GitHub/iEEG-Speech',
              '/Users/lauragwilliams/Documents/projects/iEEG-Speech']

for user_path in user_paths:
    if os.path.exists(user_path):
        base_path = user_path
        break
else:
    raise FileNotFoundError("No valid base path found.")

fig_path = os.path.join(base_path, 'vis', 'concatenated', freq, 'phoneme')
os.makedirs(fig_path, exist_ok=True)

# Create an empty dictionary to store accuracy scores
accuracy_dict = {}



for stim in stimuli:
    for run in runs:
        # Construct file path to concatenated files
        fif_path = f'{base_path}/derivatives/concatenated/{freq}/{pro}/phoneme-epo-{stim}-{run}-epo.fif'
        phoneme_path = os.path.join(base_path, 'annotations', 'phonemes', 'tsv', f'{stim}-phonemes.tsv')

        # Check if file exists
        if not os.path.exists(fif_path):
            print(f"File does not exist: {fif_path}, skipping...")
            continue

        print(f"Processing file: {fif_path}")

        # Load the epochs
        epochs = mne.read_epochs(fif_path, preload=True)

        # Downsample the epochs
        epochs.resample(100)

        # Sklearn wrapper for Logistic Regression
        clf = make_pipeline(StandardScaler(), LogisticRegression(solver='liblinear'))
        cv = KFold(5, shuffle=True)

        # Specify the desired values for decoding
        desired_phonation_value = 'v'
        desired_manner_value = 'f'
        desired_place_value = 'm'

        # Filter epochs based on desired values for decoding
        filtered_epochs_phonation = epochs[epochs.metadata['phonation'] == desired_phonation_value]
        filtered_epochs_manner = epochs[epochs.metadata['manner'] == desired_manner_value]
        filtered_epochs_place = epochs[epochs.metadata['place'] == desired_place_value]

        # Concatenate filtered epochs from all features of interest
        filtered_epochs = mne.concatenate_epochs(
            [filtered_epochs_phonation, filtered_epochs_manner, filtered_epochs_place])

        # Plotting
        fig, ax = plt.subplots(1, figsize=(10, 5))
        plt.title(f"Decoding Accuracy for {stim}_{run}")

        for feat, label, color in zip(['phonation', 'manner', 'place'], ['Voiced', 'Fricatives', 'Pure Vowel'],
                                      ['purple', 'darkviolet', 'mediumorchid']):
            desired_value = \
            {'phonation': desired_phonation_value, 'manner': desired_manner_value, 'place': desired_place_value}[feat]
            y = (filtered_epochs.metadata[feat] == desired_value).astype(int)

            # Preallocate accuracy scores array
            accuracy_scores = np.empty(filtered_epochs.get_data(copy=True).shape[-1])

            # Extract data and compute ROC-AUC scores across time
            for tt in range(accuracy_scores.shape[0]):
                X_ = filtered_epochs.get_data(copy=True)[:, :, tt]
                scores = cross_val_score(clf, X_, y, scoring='roc_auc', cv=cv, n_jobs=-1)
                accuracy_scores[tt] = scores.mean()

            ax.plot(filtered_epochs.times, accuracy_scores, label=label, color=color)

        # Add vertical dashed grey line at t=0
        ax.axvline(x=0, color='grey', linestyle='--')

        # Add horizontal dashed line at y=0.5 (chance level decoding)
        ax.axhline(y=0.5, color='grey', linestyle='--')

        ax.set_xlabel("Time (ms) relative to phoneme onset")
        ax.set_ylabel("ROC-AUC")
        ax.legend()
        plt.savefig(f'{fig_path}/{stim}_{run}_logistic.jpg', dpi=300, bbox_inches='tight')
        plt.show()

        # Save accuracy scores to a CSV file
        csv_file_path = os.path.join(base_path, 'accuracy_scores.csv')
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Key', 'Accuracy Scores'])
            for key, scores in accuracy_dict.items():
                writer.writerow([key, scores])



