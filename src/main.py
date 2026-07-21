from model_loader import ModelLoader

# Create ModelLoader object
loader = ModelLoader()

# Load model and tokenizer
model, tokenizer = loader.load_model()

print("\n✅ Model Loaded Successfully!")
print(type(model))