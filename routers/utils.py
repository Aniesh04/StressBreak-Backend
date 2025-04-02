import json
from google import genai
from google.genai.types import HttpOptions
import os
from jinja2 import Environment, FileSystemLoader
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import base64
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import numpy as np
from db.models import Journal
import pathlib
import glob
import matplotlib.dates as mdates
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

client = genai.Client(http_options=HttpOptions(api_version="v1"), api_key=os.environ.get('GOOGLE_GENAI_API_KEY')) 

# Create directory for visualizations if it doesn't exist
VISUALIZATION_DIR = './visualizations'
pathlib.Path(VISUALIZATION_DIR).mkdir(parents=True, exist_ok=True)


def create_chat():
    return client.chats.create(
        model="gemini-2.0-flash-001",
    )


def generate_struct_model_response(user_input: str) -> dict | str:
    chat = create_chat()

    llm_response = chat.send_message(user_input)

    json_text = llm_response.text.split("```json")[1].split("```")[0]
    data_dict = json.loads(json_text)
    
    return data_dict


def generate_analyze_journal(journal_content: str) -> dict:
    env = Environment(loader=FileSystemLoader("./routers")) 
    template = env.get_template('journal_analyze.j2')

    variables = { "journal_content": journal_content }
    input_prompt = template.render(variables)

    response = generate_struct_model_response(input_prompt)
    response['journal_content'] = journal_content
    
    return response


def get_user_journals_for_week(db: Session, user_id: int) -> List[Journal]:
    """
    Retrieve journal entries for the past 7 days for a specific user
    """
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    return db.query(Journal).filter(
        Journal.user_id == user_id,
        Journal.created_at >= seven_days_ago
    ).order_by(Journal.created_at).all()


def format_journal_data_for_weekly_analysis(journals: List[Journal]) -> List[Dict[str, Any]]:
    """
    Format journal data for the weekly analysis prompt
    """
    formatted_data = []
    
    for journal in journals:
        entry = {
            "journal_content": journal.journal_content,
            "emotion": {
                "happiness": journal.happiness_score,
                "sadness": journal.sadness_score,
                "fear": journal.fear_score,
                "anger": journal.anger_score,
                "surprise": journal.surprise_score,
                "joy": journal.joy_score,
                "love": journal.love_score,
                "disgust": journal.disgust_score,
                "relief": journal.relief_score,
                "gratitude": journal.gratitude_score,
                "confusion": journal.confusion_score
            },
            "sentiment": {
                "positive": journal.positive_score,
                "negative": journal.negative_score,
                "neutral": journal.neutral_score
            },
            "journal_timing": journal.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        formatted_data.append(entry)
    
    return formatted_data


def generate_weekly_analysis(journals_data: List[Dict[str, Any]]) -> dict:
    """
    Generate weekly analysis based on journal data from the past 7 days
    """
    if not journals_data:
        return {"error": "No journal entries found for the past week"}
    
    env = Environment(loader=FileSystemLoader("./routers"))
    template = env.get_template('weekly_analyze.j2')
    
    variables = {"journals_data": json.dumps(journals_data)}
    input_prompt = template.render(variables)
    
    response = generate_struct_model_response(input_prompt)
    
    # Calculate cumulative scores for visualization
    response["raw_data"] = calculate_cumulative_scores(journals_data)
    
    return response


def calculate_cumulative_scores(journals_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate cumulative scores from journal data for visualization
    """
    dates = []
    emotions = {
        "happiness": [], "sadness": [], "fear": [], "anger": [], 
        "surprise": [], "joy": [], "love": [], "disgust": [], 
        "relief": [], "gratitude": [], "confusion": []
    }
    sentiments = {"positive": [], "negative": [], "neutral": []}
    
    for entry in journals_data:
        # Extract date (just the date part)
        date_obj = datetime.strptime(entry["journal_timing"], "%Y-%m-%d %H:%M:%S")
        dates.append(date_obj.strftime("%Y-%m-%d"))
        
        # Extract emotion scores
        for emotion in emotions.keys():
            emotions[emotion].append(entry["emotion"][emotion])
        
        # Extract sentiment scores
        for sentiment in sentiments.keys():
            sentiments[sentiment].append(entry["sentiment"][sentiment])
    
    return {
        "dates": dates,
        "emotions": emotions,
        "sentiments": sentiments
    }


def save_and_encode_plot(fig, filename, format='png'):
    """
    Save plot to file and also encode it to base64
    
    Args:
        fig: matplotlib figure object
        filename: name of the file to save
        format: image format (png, jpg, etc)
        
    Returns:
        str: base64 encoded image
    """
    # Save to disk
    # full_path = os.path.join(VISUALIZATION_DIR, filename)
    # fig.savefig(full_path, format=format, dpi=100)
    
    # Save to buffer for base64 encoding
    buf = io.BytesIO()
    fig.savefig(buf, format=format)
    buf.seek(0)
    
    # Encode to base64
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    
    return img_str


def generate_emotion_plot(data: Dict[str, Any]) -> str:
    """
    Generate a line plot for emotion scores over time
    Returns base64 encoded image
    """
    plt.figure(figsize=(12, 8))
    dates = data["dates"]
    
    # Plot emotions with more than zero values
    for emotion, values in data["emotions"].items():
        if any(values):  # Only plot emotions that have non-zero values
            plt.plot(dates, values, marker='o', label=emotion.capitalize())
    
    plt.title('Weekly Emotion Trends')
    plt.xlabel('Date')
    plt.ylabel('Score (0-10)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Get user ID or timestamp for unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'emotion_plot_{timestamp}.png'
    
    # Save and encode
    img_str = save_and_encode_plot(plt, filename)
    plt.close()
    
    return img_str


def generate_emotion_grouped_plot(data: Dict[str, Any]) -> str:
    """
    Generate a grouped plot with positive, negative and other emotions separated
    Returns base64 encoded image
    """
    # Define emotion groups
    positive_emotions = ["happiness", "joy", "love", "relief", "gratitude"]
    negative_emotions = ["sadness", "fear", "anger", "disgust"]
    other_emotions = ["surprise", "confusion"]
    
    dates = data["dates"]
    
    # Create figure with subplots
    fig, axes = plt.subplots(3, 1, figsize=(12, 15), sharex=True)
    
    # Plot positive emotions
    for emotion in positive_emotions:
        values = data["emotions"][emotion]
        if any(values):  # Only plot emotions with non-zero values
            axes[0].plot(dates, values, marker='o', label=emotion.capitalize())
    
    axes[0].set_title('Positive Emotions')
    axes[0].set_ylabel('Score (0-10)')
    axes[0].grid(True, linestyle='--', alpha=0.7)
    axes[0].legend(loc='best')
    axes[0].set_ylim(0, 10)
    
    # Plot negative emotions
    for emotion in negative_emotions:
        values = data["emotions"][emotion]
        if any(values):  # Only plot emotions with non-zero values
            axes[1].plot(dates, values, marker='o', label=emotion.capitalize())
    
    axes[1].set_title('Negative Emotions')
    axes[1].set_ylabel('Score (0-10)')
    axes[1].grid(True, linestyle='--', alpha=0.7)
    axes[1].legend(loc='best')
    axes[1].set_ylim(0, 10)
    
    # Plot other emotions
    for emotion in other_emotions:
        values = data["emotions"][emotion]
        if any(values):  # Only plot emotions with non-zero values
            axes[2].plot(dates, values, marker='o', label=emotion.capitalize())
    
    axes[2].set_title('Other Emotions')
    axes[2].set_xlabel('Date')
    axes[2].set_ylabel('Score (0-10)')
    axes[2].grid(True, linestyle='--', alpha=0.7)
    axes[2].legend(loc='best')
    axes[2].set_ylim(0, 10)
    
    # Format x-axis for all subplots
    for ax in axes:
        ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    # Get timestamp for unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'emotion_grouped_plot_{timestamp}.png'
    
    # Save and encode
    img_str = save_and_encode_plot(plt, filename)
    plt.close()
    
    return img_str


def generate_emotion_heatmap(data: Dict[str, Any]) -> str:
    """
    Generate a heatmap of emotions over time
    Returns base64 encoded image
    """
    # Prepare data for heatmap
    dates = data["dates"]
    emotions = []
    emotion_values = []
    
    for emotion, values in data["emotions"].items():
        if any(values):  # Only include emotions with non-zero values
            emotions.append(emotion.capitalize())
            emotion_values.append(values)
    
    # Create a matrix for the heatmap
    heatmap_data = np.array(emotion_values)
    
    # Create figure
    plt.figure(figsize=(12, 8))
    
    # Create custom colormap (white to blue)
    cmap = LinearSegmentedColormap.from_list('custom_cmap', ['#FFFFFF', '#0571b0'], N=100)
    
    # Plot heatmap
    ax = sns.heatmap(heatmap_data, cmap=cmap, linewidths=0.5, 
                     yticklabels=emotions, xticklabels=dates, 
                     vmin=0, vmax=10, annot=True, fmt=".1f")
    
    plt.title('Emotion Intensity Heatmap')
    plt.xlabel('Date')
    plt.ylabel('Emotion')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Get timestamp for unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'emotion_heatmap_{timestamp}.png'
    
    # Save and encode
    img_str = save_and_encode_plot(plt, filename)
    plt.close()
    
    return img_str


def generate_dominant_emotions_plot(data: Dict[str, Any]) -> str:
    """
    Generate a plot showing only the top 3 emotions for each day
    Returns base64 encoded image
    """
    dates = data["dates"]
    emotions_data = data["emotions"]
    
    # Create a figure
    plt.figure(figsize=(12, 8))
    
    # Process each date
    for i, date in enumerate(dates):
        # Get emotions values for this date
        day_emotions = {emotion: emotions_data[emotion][i] for emotion in emotions_data}
        
        # Sort emotions by value and get top 3
        top_emotions = sorted(day_emotions.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Plot only the top 3 emotions for each day
        for emotion, value in top_emotions:
            if value > 0:  # Only plot non-zero values
                plt.scatter(date, value, s=100, label=f"{date} - {emotion.capitalize()}")
                plt.plot([date, date], [0, value], alpha=0.5, linestyle='--')
    
    plt.title('Dominant Emotions Each Day')
    plt.xlabel('Date')
    plt.ylabel('Score (0-10)')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.ylim(0, 10)
    plt.xticks(rotation=45)
    
    # Create a custom legend that doesn't repeat
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='upper right', 
               bbox_to_anchor=(1.15, 1), title="Top Emotions")
    
    plt.tight_layout()
    
    # Get timestamp for unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'dominant_emotions_{timestamp}.png'
    
    # Save and encode
    img_str = save_and_encode_plot(plt, filename)
    plt.close()
    
    return img_str


def generate_emotion_area_plot(data: Dict[str, Any]) -> str:
    """
    Generate a stacked area plot for emotion scores over time
    Returns base64 encoded image
    """
    # Define emotion groups
    positive_emotions = ["happiness", "joy", "love", "relief", "gratitude"]
    negative_emotions = ["sadness", "fear", "anger", "disgust"]
    
    dates = data["dates"]
    
    # Calculate aggregated values for emotion groups
    positive_values = np.zeros(len(dates))
    negative_values = np.zeros(len(dates))
    
    for emotion in positive_emotions:
        for i, val in enumerate(data["emotions"][emotion]):
            positive_values[i] += val
            
    for emotion in negative_emotions:
        for i, val in enumerate(data["emotions"][emotion]):
            negative_values[i] += val
    
    # Normalize values (optional)
    # This makes the graph show the relative proportion rather than absolute values
    # Comment out these lines if you prefer raw values
    total = positive_values + negative_values
    total = np.where(total == 0, 1, total)  # Avoid division by zero
    positive_percent = (positive_values / total) * 100
    negative_percent = (negative_values / total) * 100
    
    # Create figure
    plt.figure(figsize=(12, 7))
    
    # Plot stacked area
    plt.fill_between(dates, 0, positive_percent, label='Positive Emotions', alpha=0.7, color='#2ca02c')
    plt.fill_between(dates, positive_percent, positive_percent + negative_percent, 
                     label='Negative Emotions', alpha=0.7, color='#d62728')
    
    plt.title('Balance of Positive vs Negative Emotions')
    plt.xlabel('Date')
    plt.ylabel('Percentage of Total Emotional Intensity')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Get timestamp for unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'emotion_balance_{timestamp}.png'
    
    # Save and encode
    img_str = save_and_encode_plot(plt, filename)
    plt.close()
    
    return img_str


def generate_sentiment_plot(data: Dict[str, Any]) -> str:
    """
    Generate a line plot for sentiment scores over time
    Returns base64 encoded image
    """
    plt.figure(figsize=(10, 6))
    dates = data["dates"]
    
    # Plot sentiments
    for sentiment, values in data["sentiments"].items():
        plt.plot(dates, values, marker='o', linewidth=2, label=sentiment.capitalize())
    
    plt.title('Weekly Sentiment Analysis')
    plt.xlabel('Date')
    plt.ylabel('Score (0-10)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Get user ID or timestamp for unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'sentiment_plot_{timestamp}.png'
    
    # Save and encode
    img_str = save_and_encode_plot(plt, filename)
    plt.close()
    
    return img_str


def generate_emotion_radar_chart(data: Dict[str, Any]) -> str:
    """
    Generate a radar chart for average emotion scores
    Returns base64 encoded image
    """
    # Calculate averages for each emotion
    emotion_avgs = {}
    for emotion, values in data["emotions"].items():
        if values:  # Check if the list is not empty
            emotion_avgs[emotion] = sum(values) / len(values)
        else:
            emotion_avgs[emotion] = 0
    
    # Prepare data for radar chart
    emotions = list(emotion_avgs.keys())
    values = list(emotion_avgs.values())
    
    # Number of variables
    N = len(emotions)
    
    # Repeat the first value to close the circular graph
    values += values[:1]
    emotions += emotions[:1]
    
    # Calculate angle for each emotion
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Close the loop
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    # Draw the chart
    ax.plot(angles, values, linewidth=2, linestyle='solid')
    ax.fill(angles, values, alpha=0.25)
    
    # Set labels
    plt.xticks(angles[:-1], [e.capitalize() for e in emotions[:-1]], size=12)
    
    # Draw y-axis labels (0-10)
    ax.set_rlabel_position(0)
    plt.yticks([2, 4, 6, 8, 10], ["2", "4", "6", "8", "10"], color="grey", size=10)
    plt.ylim(0, 10)
    
    plt.title('Emotion Distribution (Weekly Average)', size=15)
    
    # Get user ID or timestamp for unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'emotion_radar_{timestamp}.png'
    
    # Save and encode
    img_str = save_and_encode_plot(plt, filename)
    plt.close()
    
    return img_str


def generate_visualizations(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate all visualizations for weekly analysis
    """
    return {
        "emotion_line_plot": generate_emotion_plot(data),
        "emotion_grouped_plot": generate_emotion_grouped_plot(data),
        "emotion_heatmap": generate_emotion_heatmap(data),
        "dominant_emotions_plot": generate_dominant_emotions_plot(data),
        "emotion_balance_plot": generate_emotion_area_plot(data),
        "sentiment_line_plot": generate_sentiment_plot(data),
        "emotion_radar_chart": generate_emotion_radar_chart(data)
    }