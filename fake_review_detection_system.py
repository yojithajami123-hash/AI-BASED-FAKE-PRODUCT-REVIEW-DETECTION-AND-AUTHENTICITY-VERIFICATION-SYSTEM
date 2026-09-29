"""
AI-Based Fake Product Review Detection and Authenticity Verification System
Detects fraudulent reviews using NLP and machine learning techniques
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

# ============================================================================
# 1. GENERATE SYNTHETIC REVIEW DATASET
# ============================================================================

def generate_review_dataset(n_reviews=1000, fake_ratio=0.3, random_state=42):
    """
    Generate synthetic product review dataset with fake and genuine reviews
    """
    np.random.seed(random_state)
    
    # Genuine review templates
    genuine_templates = [
        "Great product! Works as expected. Highly recommend.",
        "Excellent quality and fast delivery. Very satisfied.",
        "Good value for money. Will buy again.",
        "Amazing product. Exceeded my expectations.",
        "Perfect! Exactly what I needed.",
        "Fantastic quality. Highly impressed.",
        "Love it! Best purchase ever.",
        "Superb product. Highly recommended.",
        "Wonderful experience. Great customer service.",
        "Outstanding quality. Worth every penny.",
        "Fantastic! Will definitely purchase again.",
        "Excellent! Very happy with my purchase.",
        "Perfect quality and fast shipping.",
        "Amazing! Highly satisfied customer.",
        "Great value. Excellent product quality."
    ]
    
    # Fake review templates
    fake_templates = [
        "Best product ever!!!!! Amazing!!!!!",
        "5 stars 5 stars 5 stars 5 stars",
        "You must buy this now!!! Don't miss!!!",
        "Everyone should have this!!! Perfect!!!",
        "BEST EVER BEST EVER BEST EVER",
        "Amazing amazing amazing amazing!!!",
        "Buy now buy now buy now!!!",
        "Perfect perfect perfect perfect!!!",
        "Highly highly highly recommended!!!",
        "This is the best best best!!!",
        "Must have must have must have!!!",
        "Incredible incredible incredible!!!",
        "Fantastic fantastic fantastic!!!",
        "Wonderful wonderful wonderful!!!",
        "Outstanding outstanding outstanding!!!"
    ]
    
    reviews = []
    n_fake = int(n_reviews * fake_ratio)
    n_genuine = n_reviews - n_fake
    
    # Generate genuine reviews
    for i in range(n_genuine):
        template = np.random.choice(genuine_templates)
        # Add slight variations
        rating = np.random.choice([4, 5], p=[0.3, 0.7])
        reviewer_id = np.random.randint(1000, 9999)
        helpful_count = np.random.randint(0, 50)
        review_length = len(template.split())
        review_age_days = np.random.randint(1, 365)
        
        reviews.append({
            'Review_ID': i + 1,
            'Review_Text': template,
            'Rating': rating,
            'Reviewer_ID': reviewer_id,
            'Helpful_Count': helpful_count,
            'Review_Length': review_length,
            'Review_Age_Days': review_age_days,
            'Exclamation_Count': template.count('!'),
            'Capital_Ratio': sum(1 for c in template if c.isupper()) / len(template),
            'Label': 'Genuine'
        })
    
    # Generate fake reviews
    for i in range(n_fake):
        template = np.random.choice(fake_templates)
        rating = np.random.choice([1, 5], p=[0.2, 0.8])
        reviewer_id = np.random.randint(1000, 9999)
        helpful_count = np.random.randint(0, 10)
        review_length = len(template.split())
        review_age_days = np.random.randint(1, 30)  # Fake reviews typically recent
        
        reviews.append({
            'Review_ID': n_genuine + i + 1,
            'Review_Text': template,
            'Rating': rating,
            'Reviewer_ID': reviewer_id,
            'Helpful_Count': helpful_count,
            'Review_Length': review_length,
            'Review_Age_Days': review_age_days,
            'Exclamation_Count': template.count('!'),
            'Capital_Ratio': sum(1 for c in template if c.isupper()) / len(template),
            'Label': 'Fake'
        })
    
    return pd.DataFrame(reviews)

# ============================================================================
# 2. DATA EXPLORATION AND ANALYSIS
# ============================================================================

def explore_review_data(reviews_df):
    """
    Perform exploratory data analysis on review dataset
    """
    print("=" * 80)
    print("FAKE REVIEW DETECTION SYSTEM - DATASET OVERVIEW")
    print("=" * 80)
    
    print(f"\nTotal Reviews: {len(reviews_df)}")
    print(f"Genuine Reviews: {len(reviews_df[reviews_df['Label'] == 'Genuine'])}")
    print(f"Fake Reviews: {len(reviews_df[reviews_df['Label'] == 'Fake'])}")
    print(f"Fake Review Ratio: {len(reviews_df[reviews_df['Label'] == 'Fake']) / len(reviews_df):.2%}")
    
    print("\n" + "=" * 80)
    print("RATING STATISTICS")
    print("=" * 80)
    print(f"Average Rating: {reviews_df['Rating'].mean():.2f}")
    print(f"Median Rating: {reviews_df['Rating'].median():.2f}")
    print(f"Std Dev: {reviews_df['Rating'].std():.2f}")
    print(f"Min Rating: {reviews_df['Rating'].min()}")
    print(f"Max Rating: {reviews_df['Rating'].max()}")
    
    print("\n" + "=" * 80)
    print("REVIEW CHARACTERISTICS")
    print("=" * 80)
    print(f"Average Review Length: {reviews_df['Review_Length'].mean():.0f} words")
    print(f"Average Exclamation Count: {reviews_df['Exclamation_Count'].mean():.2f}")
    print(f"Average Capital Ratio: {reviews_df['Capital_Ratio'].mean():.2%}")
    print(f"Average Helpful Count: {reviews_df['Helpful_Count'].mean():.2f}")
    
    print("\n" + "=" * 80)
    print("LABEL DISTRIBUTION")
    print("=" * 80)
    print(reviews_df['Label'].value_counts())

# ============================================================================
# 3. VISUALIZATION FUNCTIONS
# ============================================================================

def create_label_distribution_plot(reviews_df):
    """Create visualization of review label distribution"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Count plot
    label_counts = reviews_df['Label'].value_counts()
    colors = ['#2ecc71', '#e74c3c']  # Green for genuine, red for fake
    ax1.bar(label_counts.index, label_counts.values, color=colors, alpha=0.8, edgecolor='black')
    ax1.set_title('Distribution of Review Labels', fontweight='bold', fontsize=12)
    ax1.set_ylabel('Count')
    ax1.grid(axis='y', alpha=0.3)
    
    # Pie chart
    ax2.pie(label_counts.values, labels=label_counts.index, autopct='%1.1f%%',
            colors=colors, startangle=90)
    ax2.set_title('Review Label Percentage', fontweight='bold', fontsize=12)
    
    plt.suptitle('Review Authenticity Distribution', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/home/ubuntu/label_distribution.png', dpi=300, bbox_inches='tight')
    print("✓ Label distribution plot saved")
    plt.close()

def create_rating_analysis_plot(reviews_df):
    """Create visualization of rating patterns"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Rating distribution by label
    genuine_ratings = reviews_df[reviews_df['Label'] == 'Genuine']['Rating'].value_counts().sort_index()
    fake_ratings = reviews_df[reviews_df['Label'] == 'Fake']['Rating'].value_counts().sort_index()
    
    x = np.arange(len(genuine_ratings))
    width = 0.35
    
    ax1.bar(x - width/2, genuine_ratings.values, width, label='Genuine', alpha=0.8, edgecolor='black')
    ax1.bar(x + width/2, fake_ratings.values, width, label='Fake', alpha=0.8, edgecolor='black')
    ax1.set_title('Rating Distribution by Review Type', fontweight='bold', fontsize=12)
    ax1.set_xlabel('Rating')
    ax1.set_ylabel('Count')
    ax1.set_xticks(x)
    ax1.set_xticklabels(genuine_ratings.index)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Average rating by label
    avg_ratings = reviews_df.groupby('Label')['Rating'].mean()
    ax2.bar(avg_ratings.index, avg_ratings.values, color=['#2ecc71', '#e74c3c'], alpha=0.8, edgecolor='black')
    ax2.set_title('Average Rating by Review Type', fontweight='bold', fontsize=12)
    ax2.set_ylabel('Average Rating')
    ax2.set_ylim([0, 5])
    ax2.grid(axis='y', alpha=0.3)
    
    plt.suptitle('Rating Pattern Analysis', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/home/ubuntu/rating_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Rating analysis plot saved")
    plt.close()

def create_linguistic_features_plot(reviews_df):
    """Create visualization of linguistic features"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Linguistic Feature Analysis', fontsize=14, fontweight='bold')
    
    # Review length distribution
    genuine_length = reviews_df[reviews_df['Label'] == 'Genuine']['Review_Length']
    fake_length = reviews_df[reviews_df['Label'] == 'Fake']['Review_Length']
    
    axes[0, 0].hist([genuine_length, fake_length], bins=20, label=['Genuine', 'Fake'], 
                    color=['#2ecc71', '#e74c3c'], alpha=0.7, edgecolor='black')
    axes[0, 0].set_title('Review Length Distribution', fontweight='bold')
    axes[0, 0].set_xlabel('Word Count')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].legend()
    axes[0, 0].grid(axis='y', alpha=0.3)
    
    # Exclamation count distribution
    genuine_excl = reviews_df[reviews_df['Label'] == 'Genuine']['Exclamation_Count']
    fake_excl = reviews_df[reviews_df['Label'] == 'Fake']['Exclamation_Count']
    
    axes[0, 1].hist([genuine_excl, fake_excl], bins=15, label=['Genuine', 'Fake'],
                    color=['#2ecc71', '#e74c3c'], alpha=0.7, edgecolor='black')
    axes[0, 1].set_title('Exclamation Mark Count Distribution', fontweight='bold')
    axes[0, 1].set_xlabel('Exclamation Count')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].legend()
    axes[0, 1].grid(axis='y', alpha=0.3)
    
    # Capital letter ratio distribution
    genuine_cap = reviews_df[reviews_df['Label'] == 'Genuine']['Capital_Ratio']
    fake_cap = reviews_df[reviews_df['Label'] == 'Fake']['Capital_Ratio']
    
    axes[1, 0].hist([genuine_cap, fake_cap], bins=20, label=['Genuine', 'Fake'],
                    color=['#2ecc71', '#e74c3c'], alpha=0.7, edgecolor='black')
    axes[1, 0].set_title('Capital Letter Ratio Distribution', fontweight='bold')
    axes[1, 0].set_xlabel('Capital Ratio')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].legend()
    axes[1, 0].grid(axis='y', alpha=0.3)
    
    # Helpful count distribution
    genuine_helpful = reviews_df[reviews_df['Label'] == 'Genuine']['Helpful_Count']
    fake_helpful = reviews_df[reviews_df['Label'] == 'Fake']['Helpful_Count']
    
    axes[1, 1].hist([genuine_helpful, fake_helpful], bins=20, label=['Genuine', 'Fake'],
                    color=['#2ecc71', '#e74c3c'], alpha=0.7, edgecolor='black')
    axes[1, 1].set_title('Helpful Count Distribution', fontweight='bold')
    axes[1, 1].set_xlabel('Helpful Count')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].legend()
    axes[1, 1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/linguistic_features.png', dpi=300, bbox_inches='tight')
    print("✓ Linguistic features plot saved")
    plt.close()

def create_model_performance_plot(results):
    """Create bar chart comparing model performance"""
    models = list(results.keys())
    accuracy = [results[m]['Accuracy'] for m in models]
    precision = [results[m]['Precision'] for m in models]
    recall = [results[m]['Recall'] for m in models]
    f1 = [results[m]['F1-Score'] for m in models]
    
    x = np.arange(len(models))
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.bar(x - 1.5*width, accuracy, width, label='Accuracy', alpha=0.8, edgecolor='black')
    ax.bar(x - 0.5*width, precision, width, label='Precision', alpha=0.8, edgecolor='black')
    ax.bar(x + 0.5*width, recall, width, label='Recall', alpha=0.8, edgecolor='black')
    ax.bar(x + 1.5*width, f1, width, label='F1-Score', alpha=0.8, edgecolor='black')
    
    ax.set_title('Model Performance Comparison', fontweight='bold', fontsize=14)
    ax.set_ylabel('Score')
    ax.set_ylim([0, 1.1])
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=15, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/model_performance.png', dpi=300, bbox_inches='tight')
    print("✓ Model performance plot saved")
    plt.close()

def create_confusion_matrix_plot(cm, model_name):
    """Create confusion matrix heatmap"""
    plt.figure(figsize=(8, 6))
    
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True,
                xticklabels=['Genuine', 'Fake'],
                yticklabels=['Genuine', 'Fake'])
    
    plt.title(f'Confusion Matrix - {model_name}', fontweight='bold', fontsize=12)
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(f'/home/ubuntu/confusion_matrix_{model_name.lower().replace(" ", "_")}.png', dpi=300, bbox_inches='tight')
    print(f"✓ Confusion matrix for {model_name} saved")
    plt.close()

def create_authenticity_score_plot(authenticity_scores, labels):
    """Create authenticity score distribution plot"""
    genuine_scores = authenticity_scores[labels == 0]
    fake_scores = authenticity_scores[labels == 1]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.hist(genuine_scores, bins=30, label='Genuine Reviews', alpha=0.7, color='#2ecc71', edgecolor='black')
    ax.hist(fake_scores, bins=30, label='Fake Reviews', alpha=0.7, color='#e74c3c', edgecolor='black')
    
    ax.set_title('Authenticity Score Distribution', fontweight='bold', fontsize=14)
    ax.set_xlabel('Authenticity Score (0-1)')
    ax.set_ylabel('Frequency')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/authenticity_scores.png', dpi=300, bbox_inches='tight')
    print("✓ Authenticity score distribution plot saved")
    plt.close()

# ============================================================================
# 4. FEATURE EXTRACTION AND MODEL TRAINING
# ============================================================================

class FakeReviewDetector:
    """
    Comprehensive fake review detection system using NLP and ML
    """
    
    def __init__(self, reviews_df):
        self.reviews_df = reviews_df
        self.models = {}
        self.results = {}
        
    def extract_features(self):
        """Extract features from reviews"""
        X = self.reviews_df[[
            'Rating', 'Review_Length', 'Exclamation_Count', 
            'Capital_Ratio', 'Helpful_Count', 'Review_Age_Days'
        ]].values
        
        y = (self.reviews_df['Label'] == 'Fake').astype(int).values
        
        return X, y
    
    def train_models(self):
        """Train multiple classification models"""
        X, y = self.extract_features()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        print("\nTraining Models...")
        
        # Logistic Regression
        print("  Training Logistic Regression...")
        lr_model = LogisticRegression(random_state=42, max_iter=1000)
        lr_model.fit(X_train, y_train)
        y_pred_lr = lr_model.predict(X_test)
        y_proba_lr = lr_model.predict_proba(X_test)[:, 1]
        
        self.models['Logistic Regression'] = lr_model
        self.results['Logistic Regression'] = {
            'Accuracy': accuracy_score(y_test, y_pred_lr),
            'Precision': precision_score(y_test, y_pred_lr, zero_division=0),
            'Recall': recall_score(y_test, y_pred_lr, zero_division=0),
            'F1-Score': f1_score(y_test, y_pred_lr, zero_division=0),
            'ROC-AUC': roc_auc_score(y_test, y_proba_lr),
            'Confusion_Matrix': confusion_matrix(y_test, y_pred_lr),
            'y_test': y_test,
            'y_pred': y_pred_lr,
            'y_proba': y_proba_lr
        }
        
        # Random Forest
        print("  Training Random Forest...")
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        y_pred_rf = rf_model.predict(X_test)
        y_proba_rf = rf_model.predict_proba(X_test)[:, 1]
        
        self.models['Random Forest'] = rf_model
        self.results['Random Forest'] = {
            'Accuracy': accuracy_score(y_test, y_pred_rf),
            'Precision': precision_score(y_test, y_pred_rf, zero_division=0),
            'Recall': recall_score(y_test, y_pred_rf, zero_division=0),
            'F1-Score': f1_score(y_test, y_pred_rf, zero_division=0),
            'ROC-AUC': roc_auc_score(y_test, y_proba_rf),
            'Confusion_Matrix': confusion_matrix(y_test, y_pred_rf),
            'y_test': y_test,
            'y_pred': y_pred_rf,
            'y_proba': y_proba_rf
        }
        
        # Gradient Boosting
        print("  Training Gradient Boosting...")
        gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        gb_model.fit(X_train, y_train)
        y_pred_gb = gb_model.predict(X_test)
        y_proba_gb = gb_model.predict_proba(X_test)[:, 1]
        
        self.models['Gradient Boosting'] = gb_model
        self.results['Gradient Boosting'] = {
            'Accuracy': accuracy_score(y_test, y_pred_gb),
            'Precision': precision_score(y_test, y_pred_gb, zero_division=0),
            'Recall': recall_score(y_test, y_pred_gb, zero_division=0),
            'F1-Score': f1_score(y_test, y_pred_gb, zero_division=0),
            'ROC-AUC': roc_auc_score(y_test, y_proba_gb),
            'Confusion_Matrix': confusion_matrix(y_test, y_pred_gb),
            'y_test': y_test,
            'y_pred': y_pred_gb,
            'y_proba': y_proba_gb
        }
        
        return self.results

# ============================================================================
# 5. MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print("\n" + "=" * 80)
    print("AI-BASED FAKE PRODUCT REVIEW DETECTION SYSTEM")
    print("=" * 80)
    
    # Generate dataset
    print("\n[Step 1] Generating Review Dataset...")
    reviews_df = generate_review_dataset(n_reviews=1000, fake_ratio=0.3)
    print(f"✓ Dataset generated with {len(reviews_df)} reviews")
    
    # Explore data
    print("\n[Step 2] Exploring Review Dataset...")
    explore_review_data(reviews_df)
    
    # Generate visualizations
    print("\n[Step 3] Generating Visualizations...")
    print("Creating label distribution plot...")
    create_label_distribution_plot(reviews_df)
    
    print("Creating rating analysis plot...")
    create_rating_analysis_plot(reviews_df)
    
    print("Creating linguistic features plot...")
    create_linguistic_features_plot(reviews_df)
    
    # Train models
    print("\n[Step 4] Training Detection Models...")
    detector = FakeReviewDetector(reviews_df)
    results = detector.train_models()
    
    # Evaluate models
    print("\n[Step 5] Evaluating Model Performance...")
    for model_name, result in results.items():
        print(f"\n{model_name}:")
        print(f"  Accuracy: {result['Accuracy']:.4f}")
        print(f"  Precision: {result['Precision']:.4f}")
        print(f"  Recall: {result['Recall']:.4f}")
        print(f"  F1-Score: {result['F1-Score']:.4f}")
        print(f"  ROC-AUC: {result['ROC-AUC']:.4f}")
    
    print("\nCreating model performance plot...")
    create_model_performance_plot(results)
    
    # Create confusion matrices
    print("Creating confusion matrices...")
    for model_name, result in results.items():
        create_confusion_matrix_plot(result['Confusion_Matrix'], model_name)
    
    # Create authenticity score plot
    print("Creating authenticity score distribution...")
    best_model_name = max(results, key=lambda x: results[x]['F1-Score'])
    authenticity_scores = results[best_model_name]['y_proba']
    labels = results[best_model_name]['y_test']
    create_authenticity_score_plot(authenticity_scores, labels)
    
    print("\n" + "=" * 80)
    print("EXECUTION COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print("\nGenerated Visualizations:")
    print("  1. label_distribution.png")
    print("  2. rating_analysis.png")
    print("  3. linguistic_features.png")
    print("  4. model_performance.png")
    print("  5. confusion_matrix_logistic_regression.png")
    print("  6. confusion_matrix_random_forest.png")
    print("  7. confusion_matrix_gradient_boosting.png")
    print("  8. authenticity_scores.png")
    
    return reviews_df, detector, results

if __name__ == "__main__":
    reviews_df, detector, results = main()
