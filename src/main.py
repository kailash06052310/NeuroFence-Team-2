from model_loader import ModelLoader

# Create ModelLoader object
loader = ModelLoader()

# Load model and tokenizer
model, tokenizer = loader.load_model()

print("\nModel Name:")
print(loader.model_name)

print("\nModel Loaded Successfully!")

from fuzzer import PromptFuzzer

# Create PromptFuzzer object
fuzzer = PromptFuzzer()

print("\nNormal Prompts:")
for prompt in fuzzer.get_normal_prompts():
    print("-", prompt)

print("\nAdversarial Prompts:")
for prompt in fuzzer.get_adversarial_prompts():
    print("-", prompt)