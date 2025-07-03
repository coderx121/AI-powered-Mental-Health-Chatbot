import pandas as pd
from transformers import GPT2Tokenizer, GPT2LMHeadModel, Trainer, TrainingArguments
import torch
from sklearn.model_selection import train_test_split
import os

# Debug: Print current directory and data folder contents
print(f"Current directory: {os.getcwd()}")
try:
    data_dir = "E:\\data"
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    print(f"CSV files in E:\\data: {csv_files}")
except Exception as e:
    print(f"Error listing files in E:\\data: {str(e)}")

# Step 1: Preprocess the dataset
def preprocess_dataset(input_path, output_path="E:\\dataset\\Mental_Health_FAQ.csv"):
    print(f"Preprocessing dataset from {input_path}")
    try:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Dataset {input_path} not found.")
        df = pd.read_csv(input_path)
        print(f"Dataset columns: {df.columns.tolist()}")

        # Rename columns to 'input' and 'response'
        if 'question' in df.columns and 'answer' in df.columns:
            df = df.rename(columns={'question': 'input', 'answer': 'response'})
        elif 'user' in df.columns and 'bot' in df.columns:
            df = df.rename(columns={'user': 'input', 'bot': 'response'})
        elif 'prompt' in df.columns and 'reply' in df.columns:
            df = df.rename(columns={'prompt': 'input', 'reply': 'response'})
        elif 'Questions' in df.columns and 'Answers' in df.columns:
            df = df.rename(columns={'Questions': 'input', 'Answers': 'response'})
        else:
            raise ValueError("Dataset must have columns like 'question'/'answer', 'user'/'bot', 'prompt'/'reply', or 'Questions'/'Answers'.")

        # Select only 'input' and 'response', remove NaNs and duplicates
        df = df[['input', 'response']].dropna().drop_duplicates()

        # Clean text: strip whitespace
        df['input'] = df['input'].astype(str).str.strip()
        df['response'] = df['response'].astype(str).str.strip()

        # Save to specified path
        df.to_csv(output_path, index=False)
        print(f"Preprocessed dataset saved to {output_path} with {len(df)} rows")
        return df
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
        return None
    except Exception as e:
        print(f"Error during preprocessing: {str(e)}")
        return None

# Step 2: Load and preprocess the dataset for training
def load_dataset(file_path):
    print(f"Loading dataset from {file_path}")
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset file {file_path} not found.")
        df = pd.read_csv(file_path)
        if 'input' not in df.columns or 'response' not in df.columns:
            raise ValueError("Dataset must have 'input' and 'response' columns.")
        df["text"] = df["input"] + " <|SEP|> " + df["response"]
        print(f"Loaded dataset with {len(df)} samples")
        return df
    except Exception as e:
        print(f"Error loading dataset: {str(e)}")
        return None

# Step 3: Tokenize the dataset
def tokenize_dataset(df, tokenizer):
    print("Tokenizing dataset")
    try:
        encodings = tokenizer(df["text"].tolist(), truncation=True, padding=True, max_length=128)
        dataset = [
            {"input_ids": torch.tensor(encodings["input_ids"][i]),
             "attention_mask": torch.tensor(encodings["attention_mask"][i]),
             "labels": torch.tensor(encodings["input_ids"][i])}
            for i in range(len(df))
        ]
        print("Dataset tokenized successfully")
        return dataset
    except Exception as e:
        print(f"Error tokenizing dataset: {str(e)}")
        return None

# Step 4: Train the model
def train_model(dataset, output_dir):
    print("Starting model training")
    try:
        tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        tokenizer.pad_token = tokenizer.eos_token
        model = GPT2LMHeadModel.from_pretrained("gpt2")

        train_data, val_data = train_test_split(dataset, test_size=0.2, random_state=42)

        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=4,
            per_device_eval_batch_size=4,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir="./logs",
            logging_steps=10,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_data,
            eval_dataset=val_data,
        )

        trainer.train()
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        print(f"Model saved to {output_dir}")
        return model, tokenizer
    except Exception as e:
        print(f"Error training model: {str(e)}")
        return None, None

# Step 5: Offline inference
def load_offline_model(model_path):
    print(f"Loading model from {model_path}")
    try:
        tokenizer = GPT2Tokenizer.from_pretrained(model_path)
        tokenizer.pad_token = tokenizer.eos_token
        model = GPT2LMHeadModel.from_pretrained(model_path)
        print("Model loaded successfully")
        return model, tokenizer
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return None, None

def chatbot_response(model, tokenizer, user_input):
    print(f"Generating response for input: {user_input}")
    try:
        input_text = "You are an empathetic mental health chatbot. Respond with kindness and support. User: " + user_input + " <|SEP|> "
        inputs = tokenizer(input_text, return_tensors="pt", padding=True, truncation=True, max_length=128)
        outputs = model.generate(
            **inputs,
            max_length=200,
            num_return_sequences=1,
            pad_token_id=tokenizer.eos_token_id,
            num_beams=5,
            no_repeat_ngram_size=2
        )
        response = tokenizer.decode(outputs[0], skip_special_tokens=False)
        response_text = response.split("<|SEP|>")[1].strip()
        return response_text + " (Note: I’m a chatbot, not a professional. Please consult a therapist for expert advice.)"
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return "Sorry, I couldn’t process that. Please try again."

# Main execution
if __name__ == "__main__":
    print("Script started")
    kaggle_dataset_path = "E:\\dataset\\Mental_Health_FAQ.csv"
    preprocessed_dataset_path = "E:\\data\\standardized_data.csv"
    output_dir = "E:\\Melo\\offline_mental_health_chatbot"

    df = preprocess_dataset(kaggle_dataset_path, preprocessed_dataset_path)
    if df is None:
        print("Preprocessing failed. Exiting.")
        exit(1)

    df = load_dataset(preprocessed_dataset_path)
    if df is None:
        print("Dataset loading failed. Exiting.")
        exit(1)

    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token
    dataset = tokenize_dataset(df, tokenizer)
    if dataset is None:
        print("Tokenization failed. Exiting.")
        exit(1)

    model, tokenizer = train_model(dataset, output_dir)
    if model is None or tokenizer is None:
        print("Training failed. Exiting.")
        exit(1)

    model, tokenizer = load_offline_model(output_dir)
    if model is None or tokenizer is None:
        print("Model loading failed. Exiting.")
        exit(1)

    print("Mental Health Chatbot is ready! Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = chatbot_response(model, tokenizer, user_input)
        print(f"Chatbot: {response}")
