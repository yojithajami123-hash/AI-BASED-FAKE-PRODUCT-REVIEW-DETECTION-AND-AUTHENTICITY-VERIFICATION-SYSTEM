"""
NLP Utilities and Review Dataset Generation for Fake Review Detection System
Provides utilities for text processing, feature extraction, and dataset generation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

class ReviewTextProcessor:
    """
    Comprehensive review text processing and NLP utilities
    """
    
    def __init__(self):
        """Initialize the review text processor"""
        self.stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        
    def count_exclamations(self, text):
        """Count exclamation marks in text"""
        return text.count('!')
    
    def count_questions(self, text):
        """Count question marks in text"""
        return text.count('?')
    
    def calculate_capital_ratio(self, text):
        """Calculate ratio of capital letters"""
        if len(text) == 0:
            return 0
        capitals = sum(1 for c in text if c.isupper())
        return capitals / len(text)
    
    def count_repeated_chars(self, text):
        """Count repeated characters (e.g., 'amaaaazing')"""
        pattern = r'(.)\1{2,}'
        matches = re.findall(pattern, text)
        return len(matches)
    
    def calculate_word_repetition(self, text):
        """Calculate word repetition score"""
        words = text.lower().split()
        if len(words) == 0:
            return 0
        
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        repeated_words = sum(1 for count in word_counts.values() if count > 1)
        return repeated_words / len(set(words)) if len(set(words)) > 0 else 0
    
    def count_urls(self, text):
        """Count URLs in text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return len(re.findall(url_pattern, text))
    
    def count_special_chars(self, text):
        """Count special characters"""
        special_chars = sum(1 for c in text if not c.isalnum() and c != ' ')
        return special_chars
    
    def calculate_sentiment_indicators(self, text):
        """Calculate sentiment indicator score"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'perfect', 'awesome']
        negative_words = ['bad', 'poor', 'terrible', 'awful', 'horrible', 'worst', 'disappointing']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        return positive_count, negative_count
    
    def extract_text_features(self, review_text):
        """
        Extract comprehensive text features from review
        """
        features = {}
        
        # Basic text metrics
        features['text_length'] = len(review_text)
        features['word_count'] = len(review_text.split())
        features['sentence_count'] = review_text.count('.') + review_text.count('!') + review_text.count('?')
        
        # Punctuation features
        features['exclamation_count'] = self.count_exclamations(review_text)
        features['question_count'] = self.count_questions(review_text)
        features['capital_ratio'] = self.calculate_capital_ratio(review_text)
        features['special_char_count'] = self.count_special_chars(review_text)
        
        # Repetition features
        features['repeated_chars'] = self.count_repeated_chars(review_text)
        features['word_repetition'] = self.calculate_word_repetition(review_text)
        
        # Content features
        features['url_count'] = self.count_urls(review_text)
        positive_count, negative_count = self.calculate_sentiment_indicators(review_text)
        features['positive_words'] = positive_count
        features['negative_words'] = negative_count
        
        # Derived features
        features['avg_word_length'] = features['text_length'] / features['word_count'] if features['word_count'] > 0 else 0
        features['punctuation_density'] = (features['exclamation_count'] + features['question_count']) / features['word_count'] if features['word_count'] > 0 else 0
        
        return features


class ReviewerBehaviorAnalyzer:
    """
    Analyze reviewer behavior patterns to detect fake reviews
    """
    
    def __init__(self):
        """Initialize the reviewer behavior analyzer"""
        pass
    
    def calculate_reviewer_consistency(self, reviewer_ratings):
        """
        Calculate consistency of reviewer ratings
        High variance in ratings suggests potential fake reviewer
        """
        if len(reviewer_ratings) < 2:
            return 0
        
        variance = np.var(reviewer_ratings)
        return variance
    
    def calculate_rating_distribution(self, reviewer_ratings):
        """
        Calculate distribution of ratings by reviewer
        Fake reviewers often give only 1s or 5s
        """
        if len(reviewer_ratings) == 0:
            return {}
        
        distribution = {}
        for rating in [1, 2, 3, 4, 5]:
            count = sum(1 for r in reviewer_ratings if r == rating)
            distribution[rating] = count / len(reviewer_ratings)
        
        return distribution
    
    def calculate_review_frequency(self, review_dates):
        """
        Calculate review frequency
        Fake reviewers often submit multiple reviews in short time periods
        """
        if len(review_dates) < 2:
            return 0
        
        sorted_dates = sorted(review_dates)
        time_diffs = []
        
        for i in range(1, len(sorted_dates)):
            diff = (sorted_dates[i] - sorted_dates[i-1]).days
            time_diffs.append(diff)
        
        if len(time_diffs) == 0:
            return 0
        
        avg_days_between = np.mean(time_diffs)
        return avg_days_between
    
    def identify_reviewer_type(self, avg_rating, rating_variance, review_count):
        """
        Identify reviewer type based on behavior
        """
        if review_count < 5:
            return 'Casual'
        elif avg_rating >= 4.5 and rating_variance < 0.5:
            return 'Enthusiast'
        elif avg_rating <= 2.5 and rating_variance < 0.5:
            return 'Critic'
        elif rating_variance > 2.0:
            return 'Varied'
        else:
            return 'Regular'


def generate_sample_reviews(n_reviews=1000, fake_ratio=0.3, random_state=42):
    """
    Generate sample review dataset with comprehensive features
    """
    processor = ReviewTextProcessor()
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
        rating = np.random.choice([4, 5], p=[0.3, 0.7])
        reviewer_id = np.random.randint(1000, 9999)
        helpful_count = np.random.randint(0, 50)
        review_age_days = np.random.randint(1, 365)
        product_id = np.random.randint(100, 999)
        
        # Extract text features
        text_features = processor.extract_text_features(template)
        
        reviews.append({
            'Review_ID': i + 1,
            'Product_ID': product_id,
            'Review_Text': template,
            'Rating': rating,
            'Reviewer_ID': reviewer_id,
            'Helpful_Count': helpful_count,
            'Review_Length': len(template),
            'Review_Age_Days': review_age_days,
            'Exclamation_Count': template.count('!'),
            'Capital_Ratio': sum(1 for c in template if c.isupper()) / len(template),
            'Word_Count': len(template.split()),
            'Repeated_Chars': text_features['repeated_chars'],
            'Word_Repetition': text_features['word_repetition'],
            'URL_Count': text_features['url_count'],
            'Positive_Words': text_features['positive_words'],
            'Negative_Words': text_features['negative_words'],
            'Punctuation_Density': text_features['punctuation_density'],
            'Label': 'Genuine'
        })
    
    # Generate fake reviews
    for i in range(n_fake):
        template = np.random.choice(fake_templates)
        rating = np.random.choice([1, 5], p=[0.2, 0.8])
        reviewer_id = np.random.randint(1000, 9999)
        helpful_count = np.random.randint(0, 10)
        review_age_days = np.random.randint(1, 30)  # Fake reviews typically recent
        product_id = np.random.randint(100, 999)
        
        # Extract text features
        text_features = processor.extract_text_features(template)
        
        reviews.append({
            'Review_ID': n_genuine + i + 1,
            'Product_ID': product_id,
            'Review_Text': template,
            'Rating': rating,
            'Reviewer_ID': reviewer_id,
            'Helpful_Count': helpful_count,
            'Review_Length': len(template),
            'Review_Age_Days': review_age_days,
            'Exclamation_Count': template.count('!'),
            'Capital_Ratio': sum(1 for c in template if c.isupper()) / len(template),
            'Word_Count': len(template.split()),
            'Repeated_Chars': text_features['repeated_chars'],
            'Word_Repetition': text_features['word_repetition'],
            'URL_Count': text_features['url_count'],
            'Positive_Words': text_features['positive_words'],
            'Negative_Words': text_features['negative_words'],
            'Punctuation_Density': text_features['punctuation_density'],
            'Label': 'Fake'
        })
    
    return pd.DataFrame(reviews)


def save_datasets(output_dir='/home/ubuntu'):
    """
    Generate and save all sample datasets
    """
    print("Generating sample review datasets...")
    
    # Generate reviews
    print("  Generating reviews dataset...")
    reviews_df = generate_sample_reviews(n_reviews=1000, fake_ratio=0.3)
    reviews_path = f'{output_dir}/sample_reviews.csv'
    reviews_df.to_csv(reviews_path, index=False)
    print(f"  ✓ Reviews saved to {reviews_path}")
    
    print("\nDataset Statistics:")
    print(f"  Total Reviews: {len(reviews_df)}")
    print(f"  Genuine Reviews: {len(reviews_df[reviews_df['Label'] == 'Genuine'])}")
    print(f"  Fake Reviews: {len(reviews_df[reviews_df['Label'] == 'Fake'])}")
    print(f"  Unique Products: {reviews_df['Product_ID'].nunique()}")
    print(f"  Unique Reviewers: {reviews_df['Reviewer_ID'].nunique()}")
    
    return reviews_df


if __name__ == '__main__':
    reviews_df = save_datasets()
    
    print("\nReview Dataset Preview:")
    print(reviews_df.head())
    
    print("\nReview Statistics:")
    print(reviews_df.describe())
    
    print("\nLabel Distribution:")
    print(reviews_df['Label'].value_counts())
    
    print("\nRating Distribution by Label:")
    print(reviews_df.groupby('Label')['Rating'].value_counts().sort_index())
