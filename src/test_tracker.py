from activation_tracker import ActivationTracker

# Create object
tracker = ActivationTracker()

# Store activation values
tracker.save_activation("Layer_1", [0.12, 0.45, 0.78])
tracker.save_activation("Layer_2", [0.31, 0.65, 0.92])

# Print one layer
print("Layer_1:")
print(tracker.get_activation("Layer_1"))

print()

# Print all layers
print("All Activations:")
print(tracker.get_all_activations())

tracker.clear_activations()

print("\nAfter Clear:")
print(tracker.get_all_activations())
