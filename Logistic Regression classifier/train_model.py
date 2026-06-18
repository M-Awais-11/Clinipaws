import pandas as pd
import os
import pickle
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import torch
from transformers import DistilBertTokenizer, DistilBertModel
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Cache path
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)
MODEL_PATH = os.path.join(CACHE_DIR, 'distilbert_lr_model.pkl')

def get_distilbert_embeddings_batched(texts, batch_size=32):
    """
    Generate DistilBERT embeddings in batches with progress bar
    """
    print("Loading DistilBERT model...")
    model_name = 'distilbert-base-uncased'
    tokenizer = DistilBertTokenizer.from_pretrained(model_name)
    model = DistilBertModel.from_pretrained(model_name)
    
    # Use GPU if available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    model.to(device)
    model.eval()
    
    all_embeddings = []
    
    print(f"Generating embeddings for {len(texts)} texts...")
    for i in tqdm(range(0, len(texts), batch_size)):
        batch_texts = texts[i:i + batch_size]
        
        # Tokenize
        inputs = tokenizer(batch_texts, return_tensors='pt', padding=True, truncation=True, max_length=64)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
            # Use [CLS] token embedding
            cls_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
            all_embeddings.append(cls_embeddings)
            
    return np.vstack(all_embeddings)

def train_and_save_model():
    print("Starting model training process...")
    
    # Load dataset
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "updated_animal_disease_dataset.csv")
    
    if not os.path.exists(csv_path):
        print(f"Error: Dataset not found at {csv_path}")
        return

    data = pd.read_csv(csv_path)
    print(f"Loaded dataset with {len(data)} rows")

    # Create text representations
    data['symptom_text'] = (
        data['animal'] + ' ' +
        data['symptom 1'].astype(str) + ' ' +
        data['symptom 2'].astype(str) + ' ' +
        data['symptom 3'].astype(str)
    )
    
    # Generate embeddings
    X_embeddings = get_distilbert_embeddings_batched(data['symptom_text'].tolist())
    
    # Encode labels
    disease_encoder = LabelEncoder()
    y_encoded = disease_encoder.fit_transform(data['disease'])
    
    # Split for validation
    X_train, X_test, y_train, y_test = train_test_split(X_embeddings, y_encoded, test_size=0.2, random_state=42)
    
    # Train Logistic Regression
    print(f"Training Logistic Regression classifier on {len(X_train)} samples...")
    lr_model = LogisticRegression(
        max_iter=2000,
        solver='lbfgs',
        random_state=42,
        C=10.0,            # Increased C for better fitting
        class_weight='balanced',  # Handle class imbalance
        n_jobs=-1          # Use all CPU cores
    )
    lr_model.fit(X_train, y_train)
    
    # Calculate metrics
    print("Calculating performance metrics...")
    y_pred = lr_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
    
    metrics = {
        'accuracy': round(accuracy * 100, 2),
        'precision': round(precision * 100, 2),
        'recall': round(recall * 100, 2),
        'f1_score': round(f1 * 100, 2)
    }
    print(f"✅ Model Metrics: Accuracy: {metrics['accuracy']}%, F1: {metrics['f1_score']}%")
    
    # Save model
    print(f"Saving model to {MODEL_PATH}...")
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump({
            'model': lr_model,
            'encoder': disease_encoder,
            'metrics': metrics
        }, f)
        
    print("✅ Model training complete and saved!")

if __name__ == "__main__":
    train_and_save_model()
